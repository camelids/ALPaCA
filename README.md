# ALPaCA

This is the original implementation of the ALPaCA WF defense
proposed in ''Website Fingerprinting Defenses at the Application Layer''
(Cherubin, Hayes, Juarez. PETS'17).

The defense can operate in a probabilistic (P-ALPaCA) or
a deterministic (D-ALPaCA) mode.

_Note: this is a research prototype. Please, do not use this code
to defend your website as yet, as it needs peer-reviewing.
We will remove this disclaimer when appropriate._

## Requirements
Coming soon.

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
