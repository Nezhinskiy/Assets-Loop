import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone


class BaseLogger(ABC):
    """
    The abstract base class for all logger classes. Defines common attributes
    and methods for all loggers.

    Attributes:
        duration (timedelta): The duration of the logger's operation.
        count_created_objects (int): The count of created objects during the
        logger's operation.
        count_updated_objects (int): The count of updated objects during the
        logger's operation.
        bank_name (str): The name of the bank related to the logger, if any.
    """
    duration: timedelta
    count_created_objects: int
    count_updated_objects: int
    bank_name = None

    def __init__(self) -> None:
        """
        Initializes the logger with the current datetime in UTC timezone and a
        logger object.
        """
        self.start_time = datetime.now(timezone.utc)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _logger_start(self) -> None:
        """
        Logs a message with the start time of the logger.
        """
        message = f'Start {self.__class__.__name__} at {self.start_time}.'
        self.logger.info(message)

    @abstractmethod
    def _get_count_created_objects(self) -> None:
        """
        Abstract method for getting the count of created objects.
        """
        pass

    @abstractmethod
    def _get_count_updated_objects(self) -> None:
        """
        Abstract method for getting the count of updated objects.
        """
        pass

    def _get_all_objects(self) -> None:
        """
        Calls _get_count_created_objects() and _get_count_updated_objects().
        """
        self._get_count_created_objects()
        self._get_count_updated_objects()

    @abstractmethod
    def _logger_end(self) -> None:
        """
        Abstract method for logging a message with the end time of the logger.
        """
        pass

    def _logger_error(self, error: Exception) -> None:
        """
        Logs an error message with the count of created and updated objects and
        the error.
        """
        self._get_all_objects()
        message = f'An error has occurred in {self.__class__.__name__}. '
        if self.bank_name is not None:
            message += f'Bank name: {self.bank_name}. '
        if self.count_created_objects + self.count_updated_objects > 0:
            message += f'Updated: {self.count_updated_objects}, '
            message += f'Created: {self.count_created_objects}. '
        else:
            message += (f'Has not been created and updated: '
                        f'{self.count_updated_objects}. ')
        message += f'{error}'
        self.logger.error(message)


class ParsingLogger(BaseLogger, ABC):
    """
    Logger for parsing operations.
    """
    def _logger_end(self) -> None:
        """
        Logs the end of the parsing logger.
        """
        self._get_all_objects()
        message = f'Finish {self.__class__.__name__} at {self.duration}. '
        if self.bank_name is not None:
            message += f'Bank name: {self.bank_name}. '
        if self.count_created_objects + self.count_updated_objects > 0:
            message += f'Updated: {self.count_updated_objects}, '
            message += f'Created: {self.count_created_objects}. '
            self.logger.info(message)
        else:
            message += (f'Has not been Created and updated: '
                        f'{self.count_updated_objects}. ')
            self.logger.info(message)


class CalculatingLogger(BaseLogger, ABC):
    """
    Logger for calculating operations.
    """
    def _logger_queue_overflowing(self):
        """
        Logs a message for a skipped task due to queue overflow.
        """
        message = (f'The task was skipped due to the accumulation of '
                   f'identical tasks in the queue. '
                   f'{self.__class__.__name__}, Bank name: {self.bank_name}.')
        self.logger.error(message)

    def _logger_end(self) -> None:
        """
        Logs the end of the calculating logger.
        """
        self._get_all_objects()
        message = (f'Finish {self.__class__.__name__} at '
                   f'{self.duration}. ')
        if self.bank_name is not None:
            message += f'Bank name: {self.bank_name}. '
        message += f'Updated: {self.count_updated_objects}, '
        message += f'Created: {self.count_created_objects}. '
        self.logger.info(message)
