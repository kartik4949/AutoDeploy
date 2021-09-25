''' a mixin class for heatbeat to rabbitmq server. '''
from time import sleep
import threading

# send heartbeat signal after 5 secs to rabbitmq.
HEART_BEAT = 5

class HeartBeatMixin:
    @staticmethod
    def _beat(connection):
        while True:
            # TODO: remove hardcode
            sleep(HEART_BEAT)
            connection.process_data_events()

    def beat(self):
        ''' process_data_events periodically. 
        TODO: hackish way, think other way.
        '''
        heartbeat = threading.Thread(
            target=self._beat, args=(self.connection,), daemon=True)
        heartbeat.start()
