#!/bin/bash

## install dependencies
## sudo apt install pandoc texlive-fonts-recommended texlive-latex-recommended
pandoc tarina-build-instructions.md -f markdown -H headerhtml -A footerhtml -o tarina-build-instructions.html
pandoc tarina-build-instructions.md -f markdown -s -o tarina-build-instructions.pdf
