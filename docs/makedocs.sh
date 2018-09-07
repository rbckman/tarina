#!/bin/bash

## install dependencies
## sudo apt install pandoc texlive-fonts-recommended texlive-latex-recommended
pandoc BUILDTARINA.md -f markdown -s -o buildtarina.index
pandoc BUILDTARINA.md -f markdown -s -o buildtarina.pdf
