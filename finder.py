from .chitayGorod import ChitaiGorod as CG


class BookFinder:
    def find(self, search_query=""):
        CG.get_books(search_query)