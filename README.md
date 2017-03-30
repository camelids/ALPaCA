# ALPaCA

This is the original implementation of the ALPaCA WF defense
proposed in ''Website Fingerprinting Defenses at the Application Layer''
(Cherubin, Hayes, Juarez. PETS'17).

The defense can operate in a probabilistic (P-ALPaCA) or
a deterministic (D-ALPaCA) mode.

_Note: this is a research prototype. Please, do not use this code
to defend your website as yet, as both code and ideas need peer-reviewing.
We will remove this disclaimer when appropriate._

## Installation
    
    # Install dependencies
    pip install -r requirements
    # Install
    python setup.py install

## Quick start (web frameworks)

The following guidelines are thought to be implemented in some web
content handler (e.g., Flask).

Imports and init sampler (we recommend caching sampler to avoid further
overheads).
    from alpaca import sampling, morph_utils, morphing, dists
    
    sampler = sampling.KDEIndividual(dists.counts, dists.html, dists.objects)

Morph an HTML page, get the result as a string.
The resulting page contains links to the original objects with the
specification of the size to what they should be padded and of their type
(e.g., "/original-object.png?type=png&size=100").
Furthermore, it may contain links to additional ("padding") objects
(e.g., "/rnd?size=100").

    html = "" # HTML page
    morphed = morphing.morph_page_distribution(html, sampler)

Pad an object (accepted as a (possibly binary) string) to the desired
size, and get the result as a string.
    content = "" # Object content
    otype = "" # Object type (e.g., css, png, ...)
    size = 0 # Target size
    morphed = morph_utils.morph_object(content, otype, 100)
    
Create a padding object of some target size.
    size = 0 # Target size
    morphed = morph_utils.create_object(size)


## P-ALPaCa
Morphing a page $PAGE.
The morphed page is put into directory $DST.
The following assumes you have generated the KDE distributions,
and put them into directory $DISTD.
You can find the distributions we used for experiments in ``data/distributions/``.

    export PAGE=                  # .html file to morph.
    export DST=                   # destination directory for the morphed page.
    export DISTD=                 # Folder containing the KDE distributions.
    
    python ssd.py --page $PAGE --dst $DST distribution --distribution-type kde --count-dist $DISTD/counts.kde --html-dist $DISTD/html.kde --objects-dist $DISTD/objects.kde
    

## D-ALPaCa
Morphing a page $PAGE.
The morphed page is put into directory $DST.

    export L=       # Parameter "lambda".
    export S=       # Parameter "sigma"
    export MAXS=    # Parameter "max_s"
    
    python ssd.py --page $PAGE --dst $DST deterministic --L $L --S $S --maxs $MAXS

## Generating custom distributions for P-ALPaCA
Coming soon.
