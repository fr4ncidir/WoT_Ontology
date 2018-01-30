# WoT Ontology Cocktail🍸
Web Of Things Thing Ontology

This repository contains
- [x] the thing description ontology as imagined by the WoT group of ARCES (Università di Bologna). It contains annotations in JSAP compliant format useful to define WoT applications.
- [x] a python script generating TD JSAP from the ontology.
- [x] a framework called Cocktail🍸 to create Things on-the-go by smart humans that know Python

This repository will contain hopefully
- [ ] Cocktail🍸 APIs in other languages
- [ ] Cocktail🍸 documentation

Please have a look in http://wot.arces.unibo.it

This ontology takes origin from the work in the following paper:   
F. Serena, M. Poveda-Villalon, and R. Garcia-Castro, “Semantic discovery in the web of things.”

# FAQs

- [ ] _I found an error in a SPARQL and I don't know how to correct it._

Just open the ontology in Protégé and modify the SPARQL. Then, run the python script tdbuilder.py to update the jsap.
Remember to push the corrections! :)