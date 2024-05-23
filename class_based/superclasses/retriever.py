from abc import abstractmethod, ABC


class Retriever(ABC):
    """
    Abstract base class for a retriever.
    """

    @abstractmethod
    def retrieve_chunks(self, question: str, n_chunks: int = 5) -> list:
        """
        Abstract method to retrieve chunks from a vector store.
        """
        pass