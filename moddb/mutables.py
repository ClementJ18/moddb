import io
import json
import os
import re
from typing import Any, Optional, Union

import bs4
from typing_extensions import Self

from .enums import AddonCategory, Licence, PlatformCategory
from .errors import ValidationError
from .pages import Game, Group, Mod
from .utils import NamedEntity, Object

file_extensions = (
    ".psd",
    ".avi",
    ".asf",
    ".mpg",
    ".mpeg",
    ".mov",
    ".mp4",
    ".wmv",
    ".iso",
    ".divx",
    ".webm",
    ".f4v",
    ".flv",
    ".m4v",
    ".mp3",
    ".wma",
    ".mid",
    ".midi",
    ".pk4",
    ".wav",
    ".doc",
    ".exe",
    ".gz",
    ".dmg",
    ".bin",
    ".mpkg",
    ".pkg",
    ".deb",
    ".jar",
    ".ace",
    ".msi",
    ".bz2",
    ".flmod",
    ".torrent",
    ".jam",
    ".run",
    ".bin",
    ".pdf",
    ".eps",
    ".ai",
    ".xls",
    ".ppt",
    ".rpm",
    ".tgz",
    ".tar",
    ".bz2",
    ".xml",
    ".conf",
    ".zip",
    ".rar",
    ".apk",
    ".7z",
    ".love",
    ".odt",
    ".ods",
    ".odp",
    ".odg",
    ".kfm",
    ".hqx",
)

thumbnail_extensions = (".gif", ".jpg", ".jpeg", ".png")


class MutableFile:
    """An object used for passing files to other functions of the library. This
    file can only be used once, after that it will need to be recreated.

    Parameters
    -----------
    fp: Union[os.PathLike, io.BufferedIOBase]
        A file-like object opened in binary mode and read mode
        or a fiepath representing a file in the hard drive to
        open.
    filename: Optional[str]
        Optional filename, must pass if you are passing a file-like
    """

    def __init__(
        self,
        fp: Union[str, bytes, os.PathLike[Any], io.BufferedIOBase],
        filename: Optional[str] = None,
    ):
        if isinstance(fp, io.IOBase):
            if not (fp.seekable() and fp.readable()):
                raise ValidationError(f"File buffer {fp!r} must be seekable and readable")
            self.fp: io.BufferedIOBase = fp
        else:
            self.fp = open(fp, "rb")

        self.filename = filename
        if filename is None:
            if isinstance(fp, str):
                _, self.filename = os.path.split(fp)
            else:
                self.filename = getattr(fp, "name")
                if self.filename is None:
                    raise ValidationError("No filename found for the passed file")


class MutableAddon:
    """This represents an addon that can be edited. You should
    use the various methods to set up the addon to look as you
    wish.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.summary = kwargs.get("summary")
        self.description = kwargs.get("description")

        self.tags = kwargs.get("tags", [])

        self.thumbnail = None

        self.file_file = None
        self.file_url = None

        self.licence = kwargs.get("licence", Licence.proprietary)
        self.credits = kwargs.get("credits")
        self.platforms = kwargs.get("platforms", [])
        self.links = kwargs.get("links", [])
        self.category = kwargs.get("category")

        # these are attributes only available when we edit
        self.name_id = kwargs.get("name_id")
        self._form_hash = kwargs.get("form_hash")
        self.url = kwargs.get("url")

    def __repr__(self):
        return f"< MutableAddon name={self.name} >"

    @classmethod
    def _from_html(cls, html: bs4.BeautifulSoup):
        category = AddonCategory(
            int(
                html.find("select", id="downloadscategory").find_all(
                    "option", {"selected": "selected"}
                )[0]["value"]
            )
        )
        name = html.find("input", id="downloadsname")["value"]
        summary = html.find("textarea", id="downloadssummary").text
        description = html.find("textarea", id="downloadsdescription").text
        licence = Licence(
            int(
                html.find("select", id="downloadslicence").find_all(
                    "option", {"selected": "selected"}
                )[0]["value"]
            )
        )
        credits = html.find("input", id="downloadscredit")["value"]
        name_id = html.find("input", id="downloadsnameid")["value"]
        tags = html.find("input", id="downloadstags")["value"].split(",")
        formhash = html.find("input", {"name": "formhash"})["value"]

        breadcrumbs = json.loads(html.find("script", type="application/ld+json").string)
        url = breadcrumbs["itemListElement"][-1]["Item"]["@id"]

        platforms = [
            PlatformCategory(platform["value"])
            for platform in html.find(id="downloadsplatforms").find_all(
                "option", selected="selected"
            )
        ]
        links = []
        for link in html.find("select", {"name": "links[]", "class": "right select"}).find_all(
            "option", selected="selected"
        ):
            link_name, link_id, link_type = re.match(
                r"([A-Za-z ]*)\|([a-z]*)([0-9]*)", link["value"]
            ).groups()
            links.append(Object(name=link_name, id=link_id, entity_type=link_type))

        return cls(
            category=category,
            name=name,
            summary=summary,
            description=description,
            platforms=platforms,
            licence=licence,
            credits=credits,
            tags=tags,
            name_id=name_id,
            form_hash=formhash,
            url=url,
            links=links,
        )

    def set_name(self, value: str) -> Self:
        """Set the name of the addon, must be between 1 and 80 characters long.

        Parameters
        -----------
        value: str
            The value to set as the name of the addon

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        name = str(value)
        if 0 >= len(name) > 80:
            raise ValidationError("Addon name must be between 1 and 80 characters long")

        self.name = name

        return self

    def set_summary(self, value: str) -> Self:
        """Set the summary of the addon, must be between 50 and 1,000 characters.

        Parameters
        ----------
        value: str
            The value to set as the summary of the addon

        Returns
        -------
        MutableAddon
            Returns itself for easy chaining
        """
        summary = str(value)
        if 50 > len(summary) > 1000:
            raise ValidationError("Addon summary must be between 50 and 1,000 characters")

        self.summary = summary

        return self

    def set_description(self, value: Union[str, None]) -> Self:
        """Set the description of the addon, must be between 50 and 1,000 characters.

        This is an optional field.

        Parameters
        ----------
        value: Union[str,None]
            The value to set as the description of the addon, or none to clear existing description

        Returns
        -------
        MutableAddon
            Returns itself for easy chaining
        """
        description = None
        if value is not None:
            description = str(value)
            if 100 > len(description):
                raise ValidationError("Addon description must be more than 100 characters")

        self.description = description

        return self

    def set_tags(self, values: Union[list[str], None]) -> Self:
        """Set the tags of the addon, sum of all tag lengths cannot be more than 400

        This is an optional field.

        Parameters
        -----------
        values: Union[list[str],None]
            The valuesto set as the tags of the addon, or none to clear existing tags

        Returns
        -------
        MutableAddon
            Returns itself for easy chaining
        """
        tags = None
        if values is not None:
            if len("".join([x.strip() for x in values])) > 400:
                raise ValidationError("Sum of all tag lengths must be less than 400")

            tags = values

        self.tags = tags

        return self

    def set_thumbnail(self, file: MutableFile) -> Self:
        """Set the thumbnail of the addon. You can pass either a file path or a file-like object.

        Parameters
        -----------
        file: MutableFile
            A file-like of the thumbnail

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        if file is not None:
            if not file.filename.endswith(thumbnail_extensions):
                raise ValidationError(
                    f"File extensions must be one of {', '.join(thumbnail_extensions)}"
                )

        self.thumbnail = file

        return self

    def set_file(self, *, file: MutableFile = None, url: str = None) -> Self:
        """Set the file of the addon. You can pass either a file path, a url or a file-like object.

        Parameters
        -----------
        file: Optional[MutableFile]
            A file-like of the file
        url: Optional[str]
            A url to the file to transfer

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        if sum([bool(file), bool(url)]) != 1:
            raise ValidationError("Must specify exactly one of file or url")

        if file is not None:
            if not file.filename.endswith(file_extensions):
                raise ValidationError(
                    f"File extensions must be one of {', '.join(file_extensions)}"
                )

        self.file_file = file
        self.file_url = url

        return self

    def set_category(self, value: AddonCategory) -> Self:
        """Set the addon category for the addon.

        Parameters
        -----------
        value: AddonCategory
            The category to set

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        self.category = value

        return self

    def set_licence(self, value: Licence) -> Self:
        """Set the addon licence for the addon.

        This is Licence.proprietary by default

        Parameters
        -----------
        value: Licence
            The licence to set

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        self.licence = value

        return self

    def set_credits(self, value: str) -> Self:
        """Set the credits of those who helped you for the addon

        This is an optional field.

        Parameters
        ----------
        value: Optional[str,None]
            The credits to set

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        credits = str(value)
        if 0 >= credits > 400:
            raise ValidationError("Credits must be between 1 and 400 characters")

        self.credits = credits

        return self

    def set_platform(self, values: list[PlatformCategory]) -> Self:
        """Set all the platforms this addon is for

        Parameters
        ----------
        values: list[PlatformCategory]
            The platforms to set

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        self.platforms = values

        return self

    def set_links(self, values: list[Union[Group, Mod, Game, Object[NamedEntity]]]) -> Self:
        """Set the entity this addon is for

        Parameters
        -----------
        values: list[Group, Mod, Game]
            The links to set

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        self.links = values

        return self

    def set_name_id(self, value: str) -> Self:
        """Set the name id for this addon.  Update only when necessary as this will
        break existing links on blogs and search engines to this content.

        This method is only useful when editing an addon

        Parameters
        -----------
        value: str
            The name id to set

        Returns
        --------
        MutableAddon
            Returns itself for easy chaining
        """
        name_id = str(value)
        if 0 >= len(name_id) > 80:
            raise ValidationError("Addon name must be between 1 and 80 characters long")

        self.name_id = name_id

        return self
