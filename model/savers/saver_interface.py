from abc import ABC, abstractmethod


class ISaver(ABC):
    """
    Interface for saving data
    """
    @abstractmethod
    def save(self, data):
        """
        Save data in a specific way.
        :param data: data to save
        """
        pass
