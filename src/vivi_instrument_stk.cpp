
#include "vivi_instrument_stk.h"

#include "stk/FileWvOut.h"
using namespace stk;
using namespace std;

//#include "stk/Clarinet.h"
#include "stk/Flute.h"


ViviInstrumentStk::ViviInstrumentStk()
{
    // Set the global sample rate before creating class instances.
    Stk::setSampleRate( 44100.0 );
    Stk::setRawwavePath( "/home/gperciva/.usr/share/stk/rawwaves/" );


    FileWvOut output;

    // Open a 16-bit, one-channel WAV formatted output file
    output.openFile( "test-instrument.wav", 1,
        FileWrite::FILE_WAV, Stk::STK_SINT16 );


    //Clarinet *clarinet = new Clarinet(220.0);
    Flute *clarinet = new Flute(220.0);
    // kill vibrato
    clarinet->controlChange(11, 0); // vibrato frequency
    clarinet->controlChange( 1, 0); // vibrato gain
    clarinet->noteOn(220, 0.0); // set up outputGain_, bug in stk?

    clarinet->setFrequency(440.0);
    clarinet->startBlowing(0.9, 1.0);
    //clarinet->noteOn(220, 0.9);
    for (int i=0; i<44100*0.5; i++) {
        output.tick( clarinet->tick() );

    }

}

ViviInstrumentStk::~ViviInstrumentStk()
{

}

