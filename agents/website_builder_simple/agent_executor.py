from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from agents.website_builder_simple.agent import WebsiteBuilderSimple
from a2a.server.tasks import TaskUpdater
from a2a.utils import (
  new_task,
  new_agent_text_message
)
import asyncio
from a2a.utils.errors import ServerError
from a2a.types import (TaskState, Task, UnsupportedOperationError )

class WebsiteBuilderSimpleAgentExecutor:
  """
  Implements the AgentExecutor interface to integrate the
  website builder simple agent with a2a framework
  """
  
  def __init__(self):
    self.agent = WebsiteBuilderSimple()
    
  async def create(self):
    await self.agent.create()

  async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
    """
    Execs the agent with the provided context and event queue
    """
    query = context.get_user_input()
    task = context.current_task
    if not task:
      task = new_task(context.message)
      await event_queue.enqueue_event(task)

    updater = TaskUpdater(event_queue, task.id, task.context_id)

    try:
      async for item in self.agent.invoke(query, task.context_id):
        is_task_complete = item.get("is_task_complete", False)

        if not is_task_complete:
          message = item.get('updates', 'The agent is still working on request')
          await updater.update_status(
            TaskState.working,
            new_agent_text_message(message, task.context_id, task.id)
          )
        else:
          final_result = item.get('content', 'no result recevied')
          await updater.update_status(
            TaskState.completed,
            new_agent_text_message(final_result, task.context_id, task.id) 
          )

          await asyncio.sleep(0.1) #time for message to be processed
    except Exception as e:
      error_message = f"An error occured: {str(e)}"
      await updater.update_status(
        TaskState.failed,
        new_agent_text_message(error_message, task.context_id, task.id)
      )
      raise 

  async def cancel(self, request: RequestContext, event_queue: EventQueue) -> Task | None:
    raise ServerError(error=UnsupportedOperationError())