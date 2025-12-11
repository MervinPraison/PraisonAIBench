try:
    from praisonaiagents import Agent
    print("Agent imported successfully")
    print(dir(Agent))
    # print help(Agent.start) if possible
except ImportError:
    print("praisonaiagents not installed")
