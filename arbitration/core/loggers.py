import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone


class BaseLogger(ABC):
    duration: timedelta
    count_created_objects: int
    count_updated_objects: int
    bank_name = None

    def __init__(self) -> None:
        self.start_time = datetime.now(timezone.utc)
        self.logger = logging.getLogger(self.__class__.__name__)

    def logger_start(self) -> None:
        message = f'Start {self.__class__.__name__} at {self.start_time}.'
        self.logger.info(message)

    @abstractmethod
    def get_count_created_objects(self) -> None:
        pass

    @abstractmethod
    def get_count_updated_objects(self) -> None:
        pass

    def get_all_objects(self) -> None:
        self.get_count_created_objects()
        self.get_count_updated_objects()

    @abstractmethod
    def logger_end(self) -> None:
        pass

    def logger_error(self, error) -> None:
        self.get_all_objects()
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
    def logger_end(self) -> None:
        self.get_all_objects()
        message = f'Finish {self.__class__.__name__} at {self.duration}. '
        if self.bank_name is not None:
            message += f'Bank name: {self.bank_name}. '
        if self.count_created_objects + self.count_updated_objects > 0:
            message += f'Updated: {self.count_updated_objects}, '
            message += f'Created: {self.count_created_objects}. '
            self.logger.error(message)
        else:
            message += (f'Has not been Created and updated: '
                        f'{self.count_updated_objects}. ')
            self.logger.error(message)


class CalculatingLogger(BaseLogger, ABC):
    def logger_end(self) -> None:
        self.get_all_objects()
        message = (f'Finish {self.__class__.__name__} at '
                   f'{self.duration}. ')
        if self.bank_name is not None:
            message += f'Bank name: {self.bank_name}. '
        message += f'Updated: {self.count_updated_objects}, '
        message += f'Created: {self.count_created_objects}. '
        self.logger.error(message)
