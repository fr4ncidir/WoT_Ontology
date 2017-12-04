# WoT_Ontology
Web Of Things Thing Ontology

This repository contains
- [x] the thing description ontology as imagined by the WoT group of ARCES (Università di Bologna)
It contains annotations in JSAP compliant format useful for define WoT applications.
- [x] a python script generating TD JSAP from the ontology.

This repository will contain hopefully
- [ ] a tool to create Thing Descriptions on-the-go by smart humans

Please have a look in http://wot.arces.unibo.it

This ontology takes origin from the work in the following paper:   
F. Serena, M. Poveda-Villalon, and R. Garcia-Castro, “Semantic discovery in the web of things.”

# FAQs

- [ ] _I found an error in a SPARQL and I don't know how to correct it._

Just open the ontology in Protégé and modify the SPARQL. Then, run the python script tdbuilder.py to update the jsap.
Remember to push the corrections! :)