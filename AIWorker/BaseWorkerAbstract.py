import abc


class BaseWorkerAbstract:
    def __init__(self):
        pass

    @abc.abstractmethod
    def init(self):
        """
        Initialize necessary settings or configurations.
        """
        pass

    @abc.abstractmethod
    def connect(self):
        """
        Establish a database connection.
        Returns False if the connection fails.
        """
        pass

    @abc.abstractmethod
    def process_line(self, line):
        """
        Process a single line from the .dlist file.
        """
        pass

    @abc.abstractmethod
    def close(self):
        """
        Close the database connection and perform any necessary cleanup.
        """
        pass

    @abc.abstractmethod
    def health_check(self):
        """
        Check the health or status of the database connection.
        """
        pass

    @abc.abstractmethod
    def reconnect(self):
        """
        Attempt to reconnect to the database if the connection drops.
        """
        pass

    @abc.abstractmethod
    def execute_batch(self, batch_commands):
        """
        Execute a batch of commands for efficiency.
        """
        pass

    @abc.abstractmethod
    def kill(self):
        """
        break all processes
        """
        pass

    @abc.abstractmethod
    def finish(self):
        """
        finish a line job for dlist
        :return:
        """
        pass
