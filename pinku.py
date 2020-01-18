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

    def __init__(self, api_key, filters=None, private_only=False, public_only=False, toread_only=False, read_only=False):
        self.buku = buku.BukuDb()
        self.pb = pinboard.Pinboard(api_key)
        self.filters = filters
        self.private_only = private_only
        self.public_only = public_only
        self.toread_only = toread_only
        self.read_only = read_only

    def import_bookmarks(self):
        """Get bookmarks from Pinboard and add them to Buku.

        Parameters
        ----------
        filters : dict
            Filters for retrieving Pinboard bookmarks.
        """

        if self.filters.get('fromdt'):
            if not self._check_update(self.filters['fromdt']):
                return

        records = self._get_pb_bookmarks()

        self._add_to_buku(records)

    def _check_update(self, date):
        """Check if there are new Pinboard bookmarks since a given date.

        Returns
        -------
        bool
            True if there are new bookmarks, else False.
        """

        last_update = self.pb.posts.update()
        if date > last_update:
            print("No Pinboard bookmarks since {}".format(last_update))
            return False
        return True

    def _get_pb_bookmarks(self):
        """Retrieves Pinboard bookmarks."""

        return self.pb.posts.all(**self.filters)

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

    def _add_to_buku(self, records):
        """Adds Pinboard bookmarks to Buku Db

        Parameters
        ----------
        rec : list
            A list of new Pinboard bookmarks to add to Buku Db.
        """

        added = 0

        for rec in records:

            if self.private_only and rec.shared:
                continue

            if self.public_only and not rec.shared:
                continue

            if self.toread_only and not rec.toread:
                continue

            if self.read_only and rec.toread:
                continue

            if self.buku.get_rec_id(rec.url) == -1:

                resp = self.buku.add_rec(rec.url,
                                         title_in=rec.description,
                                         tags_in=self._format_tags(rec.tags),
                                         desc=rec.extended)
                if resp == -1:
                    print("Could not add '{}'".format(rec))
                else:
                    added += 1

        print("Added {} bookmarks to Buku".format(added))


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


def create_pinku(api_key, **kwargs):
    """Creates a Pinku object."""

    private_only = kwargs.pop('private', None)
    public_only = kwargs.pop('public', None)
    toread_only = kwargs.pop('toread', None)
    read_only = kwargs.pop('read', None)
    filters = {k: v for k, v in kwargs.items() if v }

    return Pinku(api_key, filters=filters, private_only=private_only, public_only=public_only, toread_only=toread_only, read_only=read_only)


def main():

    pb_api_key = os.environ.get('PINBOARD_API_KEY')

    if not pb_api_key:
        print("PINBOARD_API_KEY environment variable not found")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument('--private', action='store_true', default=False,
                        help="Only retrieve bookmarks with 'shared' status")
    parser.add_argument('--public', action='store_true', default=False,
                        help="Only retrieve bookmarks without 'shared' status")
    parser.add_argument('--toread', action='store_true', default=False,
                        help="Only retrieve bookmarks with 'to read' status")
    parser.add_argument('--read', action='store_true', default=False,
                        help="Only retrieve bookmarks without 'to read' status")

    filters = parser.add_argument_group('filters')
    filters.add_argument('-t', '--tag', nargs='*',
                        help="Filter by up to three tags")
    filters.add_argument('-s', '--start',
                        help="Offset value")
    filters.add_argument('-r', '--results',
                        help="Number of results to return")
    filters.add_argument('--fromdt', type=valid_date,
                        help="Datetime. Return only bookmarks created after this time.")
    filters.add_argument('--todt', type=valid_date,
                        help="Return only bookmarks created before this time")
    filters.add_argument('--meta',
                        help="Include a change detection signature for each bookmark")


    args = parser.parse_args()
    pinku = create_pinku(pb_api_key, **vars(args))
    pinku.import_bookmarks()

if __name__ == "__main__":
    main()
