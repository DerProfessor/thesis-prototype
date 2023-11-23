from clients.RealTimeClient import RealTimeClient

class RealTimeDialogClient(RealTimeClient):

    def __init__(self, sid, socket, config):
        super().__init__(sid=sid, socket=socket, config=config)
