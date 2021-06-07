from googlesearch import search


class OnlineSearch:
    def onlineSearch(self, query):
        for i in search(query, tld='google.com', lang='en', num=10, stop=1, pause=5):
            print(i)
