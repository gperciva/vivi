
#include "vivi_instrument_stk.h"

#include "stk/FileLoop.h"
#include "stk/FileWvOut.h"
using namespace stk;
using namespace std;


ViviInstrumentStk::ViviInstrumentStk()
{
    // Set the global sample rate before creating class instances.
    Stk::setSampleRate( 44100.0 );
    Stk::setRawwavePath( "/home/gperciva/.usr/share/stk/rawwaves/" );

    FileLoop input;
    FileWvOut output;

    // Load the sine wave file.
    input.openFile( Stk::rawwavePath() + "sinewave.raw", true );

    // Open a 16-bit, one-channel WAV formatted output file
    output.openFile( "hellosine.wav", 1, FileWrite::FILE_WAV, Stk::STK_SINT16 );

    input.setFrequency( 440.0 );

    // Run the oscillator for 40000 samples, writing to the output
    // file
    for ( int i=0; i<40000; i++ )
        output.tick( input.tick() );

}

ViviInstrumentStk::~ViviInstrumentStk()
{

}

