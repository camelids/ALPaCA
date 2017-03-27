import page
import morphing
import sampling
from argparse import ArgumentParser


if __name__ == '__main__':
    
    parser = ArgumentParser(description='Server side defence.')

    parser.add_argument('--page', type=str, help='Page to morph.',
                        required=True)
    parser.add_argument('--dst', type=str, help='Destination html file.',
                        required=True)
    subparsers = parser.add_subparsers(help='Methods', dest='method')

    # Morph to target mode.
    parser_target = subparsers.add_parser('target',
                        help='Morph to look like a target page.')
    parser_target.add_argument('--target-page', type=str, 
                        help='File containing the target size of the html ' +
                             'page, and the size of the objects line by line.',
                        required=True)
    # Morph according to distribution.
    parser_distribution = subparsers.add_parser('distribution',
                        help='Morph according to distribution.')
    parser_distribution.add_argument('--distribution-type', type=str,
                        help='Histograms or KDE.', choices=['histogram', 'kde'],
                        required=True)
    parser_distribution.add_argument('--count-dist', type=str,
                        help='Sample number of objects from distribution file.',
                        required=True)
    parser_distribution.add_argument('--html-dist', type=str,
                        help='Sample HTML size from distribution file.', required=True)
    parser_distribution.add_argument('--objects-dist', type=str,
                        help='Sample sizes from distribution file.', required=True)
    # Morph deterministically.
    parser_deterministic = subparsers.add_parser('deterministic',
                        help='Morph to multiples of S and L.')
    parser_deterministic.add_argument('--S', type=int,
                        help='The size of each object is padded to the next' +
                             'multiple of S.', required=True)
    parser_deterministic.add_argument('--L', type=int,
                        help='The number of objects is padded to the next' +
                             'multiple of L.', required=True)
    parser_deterministic.add_argument('--maxs', type=int,
                        help='The maximum size of new objects (must be a ' +
                             'multiple of S.', required=True)
    # Morph with respect to size file.
    parser_file = subparsers.add_parser('file',
                    help='Morph with respect to the given size file.')
    parser_file.add_argument('--target-file', type=str,
                        help='File containing the target size of the html page,' +
                             'and the size of the objects line by line.',
                        required=True)

    args = parser.parse_args()

    if args.method == 'target':
        target = page.Page(args.target_page)
        html_size = target.html['size']
        obj_sizes = target.get_sizes()
        morphing.morph_page_target(args.page, html_size, obj_sizes, args.dst)
    elif args.method == 'distribution':
        if args.distribution_type == 'histogram':
            dist = sampling.Histogram(args.count_dist, args.html_dist,
                                      args.objects_dist)
        elif args.distribution_type == 'kde':
            dist = sampling.KDEIndividual(args.count_dist, args.html_dist,
                                          args.objects_dist)
        else:
            raise Exception("{} not recognised.".format(args.distribution_type))
        morphing.morph_page_distribution(args.page, dist, args.dst)
    elif args.method == 'deterministic':
        morphing.morph_page_deterministic(args.page, args.S, args.L, args.maxs,
                                          args.dst)
    elif args.method == 'file':
        with open(args.target_file, 'r') as f:
            sizes = f.read().strip().split()
        html_size = int(sizes[0])
        obj_sizes = [int(x) for x in sizes[1:]]
        morphing.morph_page_target(args.page, html_size, obj_sizes, args.dst)
