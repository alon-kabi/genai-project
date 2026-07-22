import os

import pymssql
import pandas as pd
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

load_dotenv(".env")


def _db_connect():
    return pymssql.connect(
        server=os.getenv("MSSQL_SERVER"),
        user=os.getenv("MSSQL_USER"),
        password=os.getenv("MSSQL_PASSWORD"),
        database=os.getenv("MSSQL_DATABASE"),
    )


def _claim_slot(cursor, position, interview_date, interview_time) -> bool:
    # Mark the Schedule row as taken (Available=0) only if it is still free.
    # Returns False when the slot is missing or already booked → prevents double-booking.
    cursor.execute(
        """
        UPDATE Schedule
        SET Available = 0
        WHERE Position = %s
        AND [Date] = %s
        AND InterviewTime = %s
        AND Available = 1
        """,
        (position, interview_date, interview_time),
    )
    return cursor.rowcount > 0


def _release_slot(cursor, position, interview_date, interview_time) -> None:
    # Free the Schedule row again so get_schedule can offer it.
    cursor.execute(
        """
        UPDATE Schedule
        SET Available = 1
        WHERE Position = %s
        AND [Date] = %s
        AND InterviewTime = %s
        """,
        (position, interview_date, interview_time),
    )


# TOOL get_schedule
@tool
def get_schedule(Position: str, month: str, year: str = "2026") -> str:
    """Return available interview slots by position, month, and year."""
    conn = None
    try:
        conn = _db_connect()

        query = """
        SELECT TOP 10
            [Date],
            InterviewTime
        FROM Schedule
        WHERE Position = %s
        AND Available = 1
        AND MONTH([Date]) = %s
        AND YEAR([Date]) = %s
        ORDER BY [Date], InterviewTime
        """

        df = pd.read_sql(query, conn, params=[Position, month, year])

        if df.empty:
            return "No available slots found."

        lines = []
        for _, row in df.iterrows():
            lines.append(f"{row['Date']} at {row['InterviewTime']}")
        return "\n".join(lines)
    except Exception as e:
        return f"FAILED: Schedule lookup error: {str(e)}"
    finally:
        # Always close so a mid-query failure does not leak the connection.
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


# TOOL - BOOK INTERVIEW
@tool
def interview_booking(
    Position: str,
    Interview_date: str,
    Interview_time: str,
    Interview_type: str,
    CandidateName: str,
    CandidatePhone: str
) -> str:
    """
    Book an interview slot into InterviewBooking.

    Required:
    - Position
    - Interview_date
    - Interview_time
    - Interview_type (Zoom or Office)
    - CandidateName
    - CandidatePhone
    """
    conn = None
    try:
        conn = _db_connect()
        cursor = conn.cursor()

        # 1) Claim the slot in Schedule first (Available 1 → 0).
        #    If nobody claimed it, abort before inserting a booking.
        if not _claim_slot(cursor, Position, Interview_date, Interview_time):
            conn.rollback()
            return "FAILED: That interview slot is no longer available."

        # 2) Record the booking only after the slot was successfully claimed.
        cursor.execute(
            """
            INSERT INTO InterviewBooking
            (
                Position,
                Interview_date,
                Interview_time,
                Interview_type,
                Status,
                CandidateName,
                CandidatePhone
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'Booked',
                %s,
                %s
            )
            """,
            (
                Position,
                Interview_date,
                Interview_time,
                Interview_type,
                CandidateName,
                CandidatePhone
            )
        )

        # 3) Commit both changes together so Schedule and InterviewBooking stay in sync.
        conn.commit()
        cursor.close()

        return (
            f"SUCCESS: Interview booked successfully. "
            f"{Position}, {Interview_date}, {Interview_time}, {Interview_type}, "
            f"{CandidateName}, {CandidatePhone}, Booked"
        )

    except Exception as e:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        return f"FAILED: Booking error: {str(e)}"
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


# TOOL - cancel_interview
@tool
def cancel_interview(Position: str, Interview_date: str, Interview_time: str) -> str:
    """Cancel an existing interview booking.

Instead of deleting the record, this tool marks the interview
as 'Cancelled' and updates the UpdatedDate timestamp."""
    conn = None
    try:
        conn = _db_connect()
        cursor = conn.cursor()

        # Soft-cancel the booking (keep the row; set Status = Cancelled).
        cursor.execute(
            """
            UPDATE InterviewBooking
            SET
                Status = 'Cancelled',
                UpdatedDate = GETDATE()
            WHERE
                Position = %s
                AND Interview_date = %s
                AND Interview_time = %s
                AND Status <> 'Cancelled'
            """,
            (
                Position,
                Interview_date,
                Interview_time
            )
        )

        updated_rows = cursor.rowcount
        if updated_rows == 0:
            conn.rollback()
            return "FAILED: No matching interview was found."

        # Put the slot back on Schedule so it can be offered again.
        _release_slot(cursor, Position, Interview_date, Interview_time)
        conn.commit()
        cursor.close()

        return (
            f"SUCCESS: Interview cancelled successfully. "
            f"{Position}, {Interview_date}, {Interview_time}"
        )

    except Exception as e:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        return f"FAILED: Cancellation error: {str(e)}"
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


# TOOL update_interview
@tool
def update_interview(
    Position: str,
    Current_date: str,
    Current_time: str,
    New_date: str,
    New_time: str,
    New_type: str
) -> str:
    """
    Update an existing interview booking.

    Use this tool when the user wants to reschedule or modify an interview.

    Required information:
    - Position
    - Current interview date
    - Current interview time
    - New interview date
    - New interview time
    - New interview type (Zoom or Office)
    """
    conn = None
    try:
        conn = _db_connect()
        cursor = conn.cursor()

        # Reschedule: claim the new Schedule slot first (unless date/time unchanged).
        same_slot = (Current_date == New_date and Current_time == New_time)
        if not same_slot:
            if not _claim_slot(cursor, Position, New_date, New_time):
                conn.rollback()
                return "FAILED: The new interview slot is no longer available."

        # Move the booking to the new date/time/type.
        cursor.execute(
            """
            UPDATE InterviewBooking
            SET
                Interview_date = %s,
                Interview_time = %s,
                Interview_type = %s,
                Status = 'Updated',
                UpdatedDate = GETDATE()
            WHERE
                Position = %s
                AND Interview_date = %s
                AND Interview_time = %s
                AND Status <> 'Cancelled'
            """,
            (
                New_date,
                New_time,
                New_type,
                Position,
                Current_date,
                Current_time
            )
        )

        updated_rows = cursor.rowcount
        if updated_rows == 0:
            # No booking matched → rollback also undoes the new-slot claim above.
            conn.rollback()
            return "FAILED: No matching interview was found."

        # Free the old Schedule slot now that the booking has moved.
        if not same_slot:
            _release_slot(cursor, Position, Current_date, Current_time)

        conn.commit()
        cursor.close()

        return (
            f"SUCCESS: Interview updated successfully.\n"
            f"Position: {Position}\n"
            f"New Date: {New_date}\n"
            f"New Time: {New_time}\n"
            f"Meeting Type: {New_type}"
        )

    except Exception as e:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        return f"FAILED: Update error: {str(e)}"
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


class ScheduleAdvisor:
    def __init__(self, llm):
        self.llm = llm
        self.tools = [get_schedule, interview_booking, update_interview, cancel_interview]
        self.executor = self.build_executor()

    def load_system_prompt(self):
        with open("prompts/schedule_prompt.txt", encoding="utf-8") as f:
            return f.read()

    def build_executor(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_system_prompt()),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def _parse_output(self, output):
        if output.strip() == "FALSE_HANDOVER":
            return {"status": "false_handover"}
        return {"status": "answered", "message": output}

    def invoke(self, conversation):
        output = self.executor.invoke({"input": conversation})["output"]
        return self._parse_output(output)
