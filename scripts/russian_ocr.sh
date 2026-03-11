#!/bin/bash
# Use tesseract to OCR mixed cyrillic/latin text from image.
tesseract -l eng+rus "$1"
