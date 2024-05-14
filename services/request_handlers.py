from fastapi import Request
from user_agents import parse


def get_user_os(request: Request):
    user_agent_str = request.headers.get('User-Agent')
    user_agent = parse(user_agent_str)
    os_info = user_agent.os.family
    return os_info
