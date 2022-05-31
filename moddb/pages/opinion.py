import re

from ..utils import concat_docs, get_date, join
from ..boxes import Thumbnail, Option
from ..enums import ThumbnailType
from .base import BaseMetaClass


@concat_docs
class Review:
    """Represents a review.

    Filtering
    -----------
    rating : int
        A value from 1 to 10 denoting the rating number you're looking for
    sitearea : Category
        The type of model the rating is for (mod, engine, game)

    Sorting
    --------
        * **ratingalt** - rating number, desc is biggest to lowest, asc is lowest to biggest
        * **memberipid** - sort reviewer account age, asc is oldest reviewer first
        * **positive** - how many people agree with it, desc is most to least people agreeing
        * **negative** - how many people disagree with it, desc is most to least people disagreeing
        * **id** - when it was added to moddb, asc is oldest, desc is most recent

    Attributes
    -----------
    id : int
        The review id
    text : str
        The contents of the review. Can be none if the member hasn't left any
    rating : int
        An int out of 10 representing the rating left with this review.
    author : Thumbnail
        A member like thumbnail of the member who left the review
    date : datetime.datetime
        Date and time of the review creation
    agree : str
            Link to agree with the review
    disagree : str
        Link to disagree with the review
    """

    def __init__(self, **attrs):
        text = attrs.get("text")
        if text:
            self.text = text.text
        else:
            self.text = None

        review = attrs.get("review")
        self.rating = int(review.span.string)

        # id and hash are none if the review doesn't have content
        try:
            strings = ("Agree", "Delete", "Disagree")
            self.id = int(
                re.findall(
                    r"siteareaid=(\d*)", review.find("a", title=strings)["href"]
                )[0]
            )
        except TypeError:
            self.id = None

        try:
            self._hash = re.findall(
                r"hash=(.*)&", review.find("a", title="Delete")["href"]
            )[0]
        except TypeError:
            self._hash = None

        author = review.div.a
        self.author = Thumbnail(
            url=author["href"],
            name=author.string.split(" ")[0],
            type=ThumbnailType.member,
        )
        self.date = get_date(review.div.span.time["datetime"])

        try:
            self.agree = join(review.find("a", title="Agree")["href"])
            self.disagree = join(review.find("a", title="Disagree")["href"])
        except TypeError:
            self.agree = None
            self.disagree = None

    def __repr__(self):
        return f"<Review author={self.author.name} rating={self.rating}>"


@concat_docs
class Poll(BaseMetaClass):
    """Represents a poll. Cannot be voted for due to restrictions implemented by the website.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
        month : Month
            The month the poll you're looking for should be from
        year : int
            A int representing a year between 2002 and now. Anything below or above 2002 will
            always return zero results.

    Sorting
    --------
        * **totalvotes** - how many people voted on the poll, desc is most to least
        * **name** - sort the poll alphabetically by name, asc is a-z
        * **date** - when it was added to moddb, asc is oldest, desc is most recent

    Attributes
    -----------
    question : str
        The question of the poll
    author : Thumbnail
        A member like thumbnail of the member who posted the poll, usually ModDB staff
    total : int
        The total number of votes that have been cast
    options : List[Option]
        The list of available options for the poll
    """

    def __init__(self, html):
        poll = html.find("div", class_="poll")
        self.question = (
            poll.parent.parent.parent.find("div", class_="normalcorner")
            .find("span", class_="heading")
            .string
        )
        self.name = self.question
        super().__init__(html)
        author = poll.find("p", class_="question").find("a")
        self.author = Thumbnail(
            name=author.string, url=author["href"], type=ThumbnailType.member
        )

        self.total = int(
            re.search(r"([\d,]*) votes", poll.find("p", class_="question").text)[
                1
            ].replace(",", "")
        )

        percentage = poll.find_all("div", class_="barouter")
        rest = poll.find_all("p")[1:]

        self.options = []
        for index, _ in enumerate(percentage):
            raw = percentage[index].div.string.replace("%", "").replace("\xa0", "")
            percent = float(f"0.{raw}")
            text = re.sub(r"\([\d,]* vote(s)?\)", "", rest[index].text)
            votes = int(
                re.search(r"([\d,]*) vote(s)?", rest[index].span.string)[1].replace(
                    ",", ""
                )
            )
            self.options.append(Option(text=text, votes=votes, percent=percent))

    def __repr__(self):
        return f"<Poll question={self.question}>"
