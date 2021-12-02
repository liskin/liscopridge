# StatsHunters Explorer Tiles live KML

<a href="https://user-images.githubusercontent.com/300342/114571388-8bc1c680-9c6e-11eb-856d-5bd567d9db27.png"><img src="https://user-images.githubusercontent.com/300342/114571388-8bc1c680-9c6e-11eb-856d-5bd567d9db27.png" height="400"></a>
<a href="https://user-images.githubusercontent.com/300342/114571408-8e242080-9c6e-11eb-9f61-0dbc721b5805.png"><img src="https://user-images.githubusercontent.com/300342/114571408-8e242080-9c6e-11eb-9f61-0dbc721b5805.png" height="400"></a>

Generates a KML with <a href="https://www.statshunters.com/faq-10-what-are-explorer-tiles">explorer tiles from statshunters.com</a> that can be used as an overlay in <a href="https://www.locusmap.app/">Locus Map</a> or Google Earth.

To use this, either deploy liscopridge yourself or use my instance here: <https://liscopridge.nomi.cz/statshunters/>

Or use the command-line interface:

## CLI usage

    $ python3 -m liscopridge.app.statshunters tiles --help
    Usage: python -m liscopridge.app.statshunters tiles [OPTIONS] SHARE_LINK
    
    Options:
      -o, --output FILENAME
      -f, --format [kml|geojson]
      -t, --types TEXT
      --individual / --no-individual  Show invidual tiles with borders (makes
                                      Locus really slow but desktop Google Earth
                                      handles it fine)
      --max-square / --no-max-square  Show max square(s)
      --help                          Show this message and exit.
