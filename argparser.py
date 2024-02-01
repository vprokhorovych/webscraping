import argparse

parser = argparse.ArgumentParser()

def positive_int(s: str):
    """Допоміжний 'тип', який пропускає лише додатні цілі числа"""
    
    num = int(s)
    if num <= 0:
        raise ValueError(" -p (--pages) value must be > 0")
    
    return num

parser.add_argument('-s', '--scrape', action='store_true', help='Start scraping now')
parser.add_argument('-b', '--backup', action='store_true', help='Start backuping now')
parser.add_argument('-a', '--all', action='store_true',
                    help='Start scraping now and after that run backuping; equivalent to setting "-s -b"'
                    )
parser.add_argument('-p', '--pages', type=positive_int,
                    help='If provided, specifies the number of pages to be scraped; of course, '
                         'first pages from the feed are taken. For testing purposes set this parameter '
                         'to small numbers, e.g. up to 5, because each (except for the last one, maybe) '
                         'page contains 100 cars and the program spends about 200 seconds for every '
                         '100 cars. If this argument is missed, then th entire feed is being scraped')

if __name__ == '__main__':
    print(parser.parse_args([]))
    # print(parser.parse_args('-p -25'.split()))
    # print(parser.parse_args('-p 1.25'.split()))
    # print(parser.parse_args('-p 25'.split()))
    # print(parser.parse_args('-p 25 -b'.split()))
    # print(parser.parse_args('-s -h'.split()))
    print(parser.parse_args('-p 30 --all -s -b'.split()))
