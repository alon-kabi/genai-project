import pymssql
import pandas as pd 
from datetime import datetime, timedelta

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool


# TOOL get_schedule 
@tool
def get_schedule (Position: str ,month:str ) -> str:
    """Return available interview slots by position and month.

    
    """
    conn = pymssql.connect(
        server="127.0.0.1",
        user="sa",
        password="MyPassw0rd!2026",
        database="Tech"
    )

    query = """
    SELECT  top  10 *
    FROM Schedule
    where Position = %s
    AND Available = 1
    AND month([Date]) = %s  
    ORDER BY [Date], InterviewTime
    
    
    """

    df = pd.read_sql(query, conn, params=[Position,month])

    conn.commit()
    conn.close()

    if df.empty:
        return "No available slots found."

    return df.to_string(index=False)


# TOOL - BOOK INTERVIEW
@tool
def interview_booking(
    Position: str,
    Interview_date: str,
    Interview_time: str,
    Interview_type :str,
    Status:str 
) -> str:
    """
    Book an interview slot and save candidate details into the database.
    and update InterviewBooking if nedded
    """

    try:

        conn = pymssql.connect(
            server="127.0.0.1",
            user="sa",
            password="MyPassw0rd!2026",
            database="Tech"
        )

        cursor = conn.cursor()

        insert_query = """
        INSERT INTO InterviewBooking
        (
            Position,
            Interview_date,
            Interview_time,
            Interview_type,
            Status 
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            'Booked'
        )
        """
        cursor.execute(
            insert_query,
            (
                Position,
                Interview_date,
                Interview_time,
                Interview_type,
                Status

            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return (
            f"SUCCESS: Interview booked successfully. "
            f"{Position}, {Interview_date}, {Interview_time},{Interview_type},{Status}"
        )

    except Exception as e:

        return f"FAILED: Booking error: {str(e)}"
    


    #TOOL - cancel_interview       
@tool
def cancel_interview(Position: str, Interview_date: str, Interview_time: str) -> str:
    """Cancel an existing interview booking.

Instead of deleting the record, this tool marks the interview
as 'Cancelled' and updates the UpdatedDate timestamp."""

    try:
        conn = pymssql.connect(
            server="127.0.0.1",
            user="sa",
            password="MyPassw0rd!2026",
            database="Tech"
        )

        cursor = conn.cursor()

        update_query = """
        UPDATE InterviewBooking
        SET
        Status = 'Cancelled',
        UpdatedDate = GETDATE()
        WHERE
        Position = %s
        AND Interview_date = %s
        AND Interview_time = %s
        AND Status <> 'Cancelled'
        """

        print("Position =", Position)
        print("Interview_date =", Interview_date)
        print("Interview_time =", Interview_time)

        cursor.execute(
            update_query,
            (
                Position,
                Interview_date,
                Interview_time
               
            )
        )

        updated_rows = cursor.rowcount 

        conn.commit()

        cursor.close()
        conn.close()

        if updated_rows == 0:
            return "FAILED: No matching interview was found."

        return (
            f"SUCCESS: Interview cancelled successfully. "
            f"{Position}, {Interview_date}, {Interview_time}"
        )

    except Exception as e:
        return f"FAILED: Cancellation error: {str(e)}"

#TOOL update_interview
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

    try:

        conn = pymssql.connect(
            server="127.0.0.1",
            user="sa",
            password="MyPassw0rd!2026",
            database="Tech"
        )

        cursor = conn.cursor()

        update_query = """
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
        """
        print("=" * 40)
        print("Position      :", Position)
        print("Current_date  :", Current_date)
        print("Current_time  :", Current_time)
        print("New_date      :", New_date)
        print("New_time      :", New_time)
        print("New_type      :", New_type)
        print("=" * 40)

          
        cursor.execute(
            update_query,
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

        conn.commit()

        cursor.close()
        conn.close()

        if updated_rows == 0:
            return (
                "FAILED: No matching interview was found."
            )

        return (
            f"SUCCESS: Interview updated successfully.\n"
            f"Position: {Position}\n"
            f"New Date: {New_date}\n"
            f"New Time: {New_time}\n"
            f"Meeting Type: {New_type}"
        )

    except Exception as e:

        return f"FAILED: Update error: {str(e)}"


class ScheduleAdvisor:
    def __init__(self, llm):
        self.llm = llm
        self.tools = [get_schedule,interview_booking,update_interview,cancel_interview]
        self.executor = self.build_executor()

    def load_system_prompt(self):
        with open("prompts/SchedualeAdvisor_prompt.txt") as f:
            return f.read()

    def build_executor(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_system_prompt()),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", "{input}"),
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)

    def _parse_output(self, output):
        if output.strip() == "FALSE_HANDOVER":
            return {"status": "false_handover"}
        return {"status": "answered", "message": output}

    def invoke(self, conversation):
        output = self.executor.invoke({"input": conversation})["output"]
        return self._parse_output(output)
