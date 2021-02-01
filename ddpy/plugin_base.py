from abc import ABCMeta, abstractmethod


class GetPluginBase(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def get_data(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def check_cache(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def save_cache(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class GivePluginBase(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def give_data(self, *args, **kwargs) -> None:
        raise NotImplementedError()
