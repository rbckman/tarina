#!/bin/bash

## install dependencies
#sudo apt install -y pandoc texlive-fonts-recommended texlive-latex-recommended
pandoc tarina-build-instructions.md -f markdown -V keywords="Camera, 3d Printed, Filmmaker, Raspberry pi" -V title-prefix="Tarina" -V css="style.css" -V pagetitle="a 3d printable camera for lazy filmmakers" -s -o tarina-build-instructions.html
pandoc tarina-build-instructions.md -f markdown -V papersize:a4 -V geometry:margin=0.8in -s -o tarina-build-instructions.pdf
