#!/usr/bin/env python3

import argparse
import datetime
import os

import buku
import pinboard

class Pinku(object):
    """Retrieves Pinboard bookmarks adds them to a Buku database.

    Parameters
    ----------
    api_key : str
        Pinboard API key

    Attributes
    ----------
    buku : A Buku Db object
    pb : a Pinboard API wrapper object
    """

    def __init__(self, api_key):
        self.buku = buku.BukuDb()
        self.pb = pinboard.Pinboard(api_key)

    def add(self, filters):
        """Get bookmarks from Pinboard and add them to Buku.

        Parameters
        ----------
        filters : dict
            Filters for retrieving Pinboard bookmarks.
        """

        filters = {k: v for k, v in vars(filters).items() if v }

        if filters.get('fromdt'):
            last_update = self._check_update():
            if last_update > filters['fromdt']:
                print("No Pinboard bookmarks since {}".format())
                return

        records = self._get_pb_bookmarks(**filters)
        print(records)
        return
        added = 0
        for rec in records:
            if self.buku.get_rec_id(rec.url) == -1:
                resp = self._add_to_buku(rec)
                if resp == -1:
                    print("Could not add '{}'".format(rec))
                else:
                    added += 1

        print("Added {} bookmarks to Buku".format(added))

    def _check_update(self):
        """Return most recent time a bookmark was added to Pinboard."""
        return self.pb.posts.update()

    def _get_pb_bookmarks(self, **kwargs):
        """Retrieves Pinboard bookmarks."""

        return self.pb.posts.all(**kwargs)

    def _format_tags(self, tags):
        """Formats tags to conform to Buku style.

        Tags are wrapped anddelimited by commas.

        Parameters
        ----------
        tags : list
            List of Pinboard tags for a given bookmark.

        Returns
        -------
        str
            Comma delimited string of tags.
        """

        tags = ',{},'.format(','.join(tags))
        return tags

    def _add_to_buku(self, rec):
        """Adds Pinboard bookmarks to Buku Db

        Parameters
        ----------
        rec : Pinboard Bookmark object
            A new Pinboard bookmark to add to Buku Db.
        """
        return self.buku.add_rec(rec.url,
                                 title_in=rec.description,
                                 tags_in=self._format_tags(rec.tags),
                                 desc=rec.extended)

def valid_date(date):
    """Convert date string to Datetime object.

    Parameters
    ----------
    date : str
        User supplied date.

    Returns
    -------
    Datetime object
    """
    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.\nDates must be in 'Year-month-day' format".format(date)
        raise argparse.ArgumentTypeError(msg)


def main():

    pb_api_key = os.environ.get('PINBOARD_API_KEY')

    if not pb_api_key:
        print("PINBOARD_API_KEY environment variable not found")
        return

    pinku = Pinku(pb_api_key)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tag', nargs='*', help="Filter by up to three tag")
    parser.add_argument('-s', '--start', help="Offset value")
    parser.add_argument('-r', '--results', help="Number of results to return")
    parser.add_argument('--fromdt', type=valid_date,
                        help="Datetime. Return only bookmarks created after this time.")
    parser.add_argument('--todt', type=valid_date,
                        help="Return only bookmarks created before this time")

    args = parser.parse_args()
    pinku.add(args)


if __name__ == "__main__":
    main()