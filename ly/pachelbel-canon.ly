%=============================================
%   created by MuseScore Version: 1.2
%          Friday, 1 February 2013
%=============================================

\version "2.12.0"

\pointAndClickOff


%\include "reduce-whitespace.ly"
#(set-global-staff-size 16)

AVlnvoiceAA = \relative c'{
    \set Staff.instrumentName = #"violin-1"
    \set Staff.shortInstrumentName = #"Vln. 1"
    \clef treble
    %staffkeysig
    \key d \major 
    %barkeysig: 
    \key d \major 
    %bartimesig: 
    \time 4/4 
    \tempo 4 = 46
    r1 r1
     | % 
    fis'4\mp e d cis      | % 3
    b a b cis      | % 4
    d cis b a      | % 5
    g fis g e      | % 6
    d8( fis) a( g) fis( d) fis( e)      | % 7
    d( b) d( a') g( b) a( g)      | % 8
    fis( d) e( cis') d( fis) a( a,)      | % 9
    b( g) a( fis) d d' d8.\trill  cis16      | % 10
    d cis d d, cis a' e fis d d' cis b cis fis a b      | % 11
    g fis e g fis e d cis b a g fis e g fis e      | % 12
    d e fis g a e a g fis b a g a g fis e      | % 13
    d b b' cis d cis b a g fis e b' a b a g      | % 14
    fis8 fis'-|  e4--  r8 d-. \downbow  fis4      | % 15
    b a b cis      | % 16
    d8-|  d,-.  cis4 r8 b-. \downbow  d4      | % 17
    d4. d8 d--  g--  e--  a--       | % 18
    a16( fis32 g) a16( fis32 g) a-.  a,( b cis d e fis g) fis16( d32 e) fis16-.  fis,32( g) a( b a g a fis g a)      | % 19
    g16( b32 a g16 fis32 e) fis( e d e fis g a b) g16( b32 a b16 cis32 d) a( b cis d e fis g a)      | % 20
    fis16( d32 e fis16 e32 d) e( cis d e fis e d cis) d16( b32 cis) d16-.  d,32( e) fis( g fis e fis d' cis d)      | % 21
    b16( d32 cis b16 a32 g) a( g fis g a b cis d) b16( d32 cis d16 cis32 b) cis( d e d cis d b cis)      | % 22
    d8-|  r cis-|  r b-|  r d-|  r      | % 23
    d,-|  r d-|  r d-|  r e-|  r      | % 24
    r a-.  r a-.  r fis-.  r a-.       | % 25
    r g-.  r fis-.  r g-.  r e'-.       | % 26
    fis16-|  fis, g fis e-|  e' fis e d-|  fis, d b' a-|  a, g a      | % 27
    b-|  b' cis b a-|  a, g a b-|  b' a b cis-|  cis, b cis      | % 28
    d-|  d' e d cis-|  cis, d cis b-|  b' a b cis-|  cis, fis e      | % 29
    d-|  d' e g fis-|  fis, a fis' d-|  g fis g e-|  a, g a      | % 30
    fis a a a a a a a fis fis fis fis fis fis a a      | % 31
    g g g d' d d d d d d b b a a e' cis      | % 32
    a fis' fis fis e e e e d d d d a' a a a      | % 33
    b b b b a a a a b b b b cis cis, cis cis      | % 34
    d-|  d,32( e fis16) d-.  cis-|  cis'32( d e16) cis-.  b-|  b,32( cis d16) b-.  cis-|  a'32( g fis16) e-.       | % 35
    d-|  g32( fis e16) g-.  fis-|  d32( e fis16) a-.  g-|  b32( a g16) fis-.  e-|  a32( g fis16) e-.       | % 36
    fis-|  d'32( cis d16) fis,-.  a-|  a32( b cis16) a-.  fis-|  d'32( e fis16) d-.  fis-|  fis32( e d16) cis-.       | % 37
    b-|  b32( a b16) cis-.  d-|  fis32( e d16) fis-.  g-|  d32( cis b16) b-.  a e a a      | % 38
    a4. a8 d,4. a'8      | % 39
    g4 a g8 d d8.\trill  cis16      | % 40
    d8 d'\downbow  cis4--  b--  a--       | % 41
    d,8. e16 fis4--  b--  e,8. e16      | % 42
    fis8. fis'16 fis( g) fis( e) d8. d16 d( e) d( cis)      | % 43
    b4 d d16( c) b( c) a8. a16      | % 44
    a8. a'16 a( b) a( g) fis8. fis16 fis( g) fis( e)      | % 45
    d( c) b( c) a8. a16 g8 d' cis8. cis16      | % 46
    d8 d4\downbow  cis b a8~      | % 47
    a g4 fis8~ fis8. e16 e4      | % 48
    fis8 fis'4 e8 d d'4 c8      | % 49
    b4 d8( a) b4 a      | % 50
    a a,8.( g16) fis4 fis'8.( e16)      | % 51
    d4. d8 d4 cis      | % 52
    d8--  d,--  cis--  cis'--  b--  b,--  a--  a'--       | % 53
    g--  g'--  fis--  fis,--  e--  b'--  e,--  e'--       | % 54
    fis fis, e e' d d, cis cis'      | % 55
    b b' a a, g8. e'16 a,8 a     | % 56
    a4\fermata  r r2 \bar "|." 
}% end of last bar in partorvoice

 

AVlnvoiceBA = \relative c'{
    \set Staff.instrumentName = #"violin-2"
    \set Staff.shortInstrumentName = #"Vln. 2"
    \clef treble
    %staffkeysig
    \key d \major 
    %barkeysig: 
    \key d \major 
    %bartimesig: 
    \tempo 4 = 46
    \time 4/4 
    r1 r r r | % 
    fis'4\mp e d cis      | % 5
    b a b cis      | % 6
    d cis b a      | % 7
    g fis g e      | % 8
    d8( fis) a( g) fis( d) fis( e)      | % 9
    d( b) d( a') g( b) a( g)      | % 10
    fis( d) e( cis') d( fis) a( a,)      | % 11
    b( g) a( fis) d d' d8.\trill  cis16      | % 12
    d cis d d, cis a' e fis d d' cis b cis fis a b      | % 13
    g fis e g fis e d cis b a g fis e g fis e      | % 14
    d e fis g a e a g fis b a g a g fis e      | % 15
    d b b' cis d cis b a g fis e b' a b a g      | % 16
    fis8 fis'-|  e4--  r8 d-. \downbow  fis4      | % 17
    b a b cis      | % 18
    d8-|  d,-.  cis4 r8 b-. \downbow  d4      | % 19
    d4. d8 d--  g--  e--  a--       | % 20
    a16( fis32 g) a16( fis32 g) a-.  a,( b cis d e fis g) fis16( d32 e) fis16-.  fis,32( g) a( b a g a fis g a)      | % 21
    g16( b32 a g16 fis32 e) fis( e d e fis g a b) g16( b32 a b16 cis32 d) a( b cis d e fis g a)      | % 22
    fis16( d32 e fis16 e32 d) e( cis d e fis e d cis) d16( b32 cis) d16-.  d,32( e) fis( g fis e fis d' cis d)      | % 23
    b16( d32 cis b16 a32 g) a( g fis g a b cis d) b16( d32 cis d16 cis32 b) cis( d e d cis d b cis)      | % 24
    d8-|  r cis-|  r b-|  r d-|  r      | % 25
    d,-|  r d-|  r d-|  r e-|  r      | % 26
    r a-.  r a-.  r fis-.  r a-.       | % 27
    r g-.  r fis-.  r g-.  r e'-.       | % 28
    fis16-|  fis, g fis e-|  e' fis e d-|  fis, d b' a-|  a, g a      | % 29
    b-|  b' cis b a-|  a, g a b-|  b' a b cis-|  cis, b cis      | % 30
    d-|  d' e d cis-|  cis, d cis b-|  b' a b cis-|  cis, fis e      | % 31
    d-|  d' e g fis-|  fis, a fis' d-|  g fis g e-|  a, g a      | % 32
    fis a a a a a a a fis fis fis fis fis fis a a      | % 33
    g g g d' d d d d d d b b a a e' cis      | % 34
    a fis' fis fis e e e e d d d d a' a a a      | % 35
    b b b b a a a a b b b b cis cis, cis cis      | % 36
    d-|  d,32( e fis16) d-.  cis-|  cis'32( d e16) cis-.  b-|  b,32( cis d16) b-.  cis-|  a'32( g fis16) e-.       | % 37
    d-|  g32( fis e16) g-.  fis-|  d32( e fis16) a-.  g-|  b32( a g16) fis-.  e-|  a32( g fis16) e-.       | % 38
    fis-|  d'32( cis d16) fis,-.  a-|  a32( b cis16) a-.  fis-|  d'32( e fis16) d-.  fis-|  fis32( e d16) cis-.       | % 39
    b-|  b32( a b16) cis-.  d-|  fis32( e d16) fis-.  g-|  d32( cis b16) b-.  a e a a      | % 40
    a4. a8 d,4. a'8      | % 41
    g4 a g8 d d8.\trill  cis16      | % 42
    d8 d'\downbow  cis4--  b--  a--       | % 43
    d,8. e16 fis4--  b--  e,8. e16      | % 44
    fis8. fis'16 fis( g) fis( e) d8. d16 d( e) d( cis)      | % 45
    b4 d d16( c) b( c) a8. a16      | % 46
    a8. a'16 a( b) a( g) fis8. fis16 fis( g) fis( e)      | % 47
    d( c) b( c) a8. a16 g8 d' cis8. cis16      | % 48
    d8 d4\downbow  cis b a8~      | % 49
    a g4 fis8~ fis8. e16 e4      | % 50
    fis8 fis'4 e8 d d'4 c8      | % 51
    b4 d8( a) b4 a      | % 52
    a a,8.( g16) fis4 fis'8.( e16)      | % 53
    d4. d8 d4 cis      | % 54
    d8--  d,--  cis--  cis'--  b--  b,--  a--  a'--       | % 55
    g--  g'--  fis--  fis,--  e--  b'--  e,--  e'--     | % 56
    fis4\fermata  r r2 \bar "|." 
}% end of last bar in partorvoice

 

AVlnvoiceCA = \relative c'{
    \set Staff.instrumentName = #"violin-3"
    \set Staff.shortInstrumentName = #"Vln. 3"
    \clef treble
    %staffkeysig
    \key d \major 
    %barkeysig: 
    \key d \major 
    %bartimesig: 
    \tempo 4 = 46
    \time 4/4 
    r1 r r r r r  | % 
    fis'4\mp e d cis      | % 7
    b a b cis      | % 8
    d cis b a      | % 9
    g fis g e      | % 10
    d8( fis) a( g) fis( d) fis( e)      | % 11
    d( b) d( a') g( b) a( g)      | % 12
    fis( d) e( cis') d( fis) a( a,)      | % 13
    b( g) a( fis) d d' d8.\trill  cis16      | % 14
    d cis d d, cis a' e fis d d' cis b cis fis a b      | % 15
    g fis e g fis e d cis b a g fis e g fis e      | % 16
    d e fis g a e a g fis b a g a g fis e      | % 17
    d b b' cis d cis b a g fis e b' a b a g      | % 18
    fis8 fis'-|  e4--  r8 d-. \downbow  fis4      | % 19
    b a b cis      | % 20
    d8-|  d,-.  cis4 r8 b-. \downbow  d4      | % 21
    d4. d8 d--  g--  e--  a--       | % 22
    a16( fis32 g) a16( fis32 g) a-.  a,( b cis d e fis g) fis16( d32 e) fis16-.  fis,32( g) a( b a g a fis g a)      | % 23
    g16( b32 a g16 fis32 e) fis( e d e fis g a b) g16( b32 a b16 cis32 d) a( b cis d e fis g a)      | % 24
    fis16( d32 e fis16 e32 d) e( cis d e fis e d cis) d16( b32 cis) d16-.  d,32( e) fis( g fis e fis d' cis d)      | % 25
    b16( d32 cis b16 a32 g) a( g fis g a b cis d) b16( d32 cis d16 cis32 b) cis( d e d cis d b cis)      | % 26
    d8-|  r cis-|  r b-|  r d-|  r      | % 27
    d,-|  r d-|  r d-|  r e-|  r      | % 28
    r a-.  r a-.  r fis-.  r a-.       | % 29
    r g-.  r fis-.  r g-.  r e'-.       | % 30
    fis16-|  fis, g fis e-|  e' fis e d-|  fis, d b' a-|  a, g a      | % 31
    b-|  b' cis b a-|  a, g a b-|  b' a b cis-|  cis, b cis      | % 32
    d-|  d' e d cis-|  cis, d cis b-|  b' a b cis-|  cis, fis e      | % 33
    d-|  d' e g fis-|  fis, a fis' d-|  g fis g e-|  a, g a      | % 34
    fis a a a a a a a fis fis fis fis fis fis a a      | % 35
    g g g d' d d d d d d b b a a e' cis      | % 36
    a fis' fis fis e e e e d d d d a' a a a      | % 37
    b b b b a a a a b b b b cis cis, cis cis      | % 38
    d-|  d,32( e fis16) d-.  cis-|  cis'32( d e16) cis-.  b-|  b,32( cis d16) b-.  cis-|  a'32( g fis16) e-.       | % 39
    d-|  g32( fis e16) g-.  fis-|  d32( e fis16) a-.  g-|  b32( a g16) fis-.  e-|  a32( g fis16) e-.       | % 40
    fis-|  d'32( cis d16) fis,-.  a-|  a32( b cis16) a-.  fis-|  d'32( e fis16) d-.  fis-|  fis32( e d16) cis-.       | % 41
    b-|  b32( a b16) cis-.  d-|  fis32( e d16) fis-.  g-|  d32( cis b16) b-.  a e a a      | % 42
    a4. a8 d,4. a'8      | % 43
    g4 a g8 d d8.\trill  cis16      | % 44
    d8 d'\downbow  cis4--  b--  a--       | % 45
    d,8. e16 fis4--  b--  e,8. e16      | % 46
    fis8. fis'16 fis( g) fis( e) d8. d16 d( e) d( cis)      | % 47
    b4 d d16( c) b( c) a8. a16      | % 48
    a8. a'16 a( b) a( g) fis8. fis16 fis( g) fis( e)      | % 49
    d( c) b( c) a8. a16 g8 d' cis8. cis16      | % 50
    d8 d4\downbow  cis b a8~      | % 51
    a g4 fis8~ fis8. e16 e4      | % 52
    fis8 fis'4 e8 d d'4 c8      | % 53
    b4 d8( a) b4 a      | % 54
    a a,8.( g16) fis4 fis'8.( e16)      | % 55
    d4. d8 d4 cis     | % 56
    d4\fermata  r r2 \bar "|." 
}% end of last bar in partorvoice

 

AVlcvoiceDA = \relative c{
    \set Staff.instrumentName = #"cello-1"
    \set Staff.shortInstrumentName = #"Vlc."
    \clef bass
    %staffkeysig
    \key d \major 
    %barkeysig: 
    \key d \major 
    %bartimesig: 
    \tempo 4 = 46
    \time 4/4 
    d4\mp a b fis      | % 1
    g d g a      | % 2
    d\p a b fis      | % 3
    g d g a      | % 4
    d a b fis      | % 5
    g d g a      | % 6
    d a b fis      | % 7
    g d g a      | % 8
    d a b fis      | % 9
    g d g a      | % 10
    d a b fis      | % 11
    g d g a      | % 12
    d a b fis      | % 13
    g d g a      | % 14
    d a b fis      | % 15
    g d g a      | % 16
    d a b fis      | % 17
    g d g a      | % 18
    d a b fis      | % 19
    g d g a      | % 20
    d a b fis      | % 21
    g d g a      | % 22
    d a b fis      | % 23
    g d g a      | % 24
    d a b fis      | % 25
    g d g a      | % 26
    d a b fis      | % 27
    g d g a      | % 28
    d a b fis      | % 29
    g d g a      | % 30
    d a b fis      | % 31
    g d g a      | % 32
    d a b fis      | % 33
    g d g a      | % 34
    d a b fis      | % 35
    g d g a      | % 36
    d a b fis      | % 37
    g d g a      | % 38
    d a b fis      | % 39
    g d g a      | % 40
    d a b fis      | % 41
    g d g a      | % 42
    d a b fis      | % 43
    g d g a      | % 44
    d a b fis      | % 45
    g d g a      | % 46
    d a b fis      | % 47
    g d g a      | % 48
    d a b fis      | % 49
    g d g a      | % 50
    d a b fis      | % 51
    g d g a      | % 52
    d a b fis      | % 53
    g d g a      | % 54
    d a b fis      | % 55
    g d g a     | % 56
    d4\fermata  r r2 \bar "|." 
}% end of last bar in partorvoice


\book{
\score { 
    << 
        \context Staff = AVlnpartA << 
            \context Voice = AVlnvoiceAA \AVlnvoiceAA
        >>


        \context Staff = AVlnpartB << 
            \context Voice = AVlnvoiceBA \AVlnvoiceBA
        >>


        \context Staff = AVlnpartC << 
            \context Voice = AVlnvoiceCA \AVlnvoiceCA
        >>


        \context Staff = AVlcpartD << 
            \context Voice = AVlcvoiceDA \AVlcvoiceDA
        >>




      \set Score.skipBars = ##t
      %%\set Score.melismaBusyProperties = #'()
      % \override Score.BarNumber #'break-visibility = #end-of-line-invisible %%every bar is numbered.!!!
      %% remove previous line to get barnumbers only at beginning of system.
       #(set-accidental-style 'modern-cautionary)
      \set Score.markFormatter = #format-mark-box-letters %%boxed rehearsal-marks
       \override Score.TimeSignature #'style = #'() %%makes timesigs always numerical
      %% remove previous line to get cut-time/alla breve or common time 
      \set Score.pedalSustainStyle = #'mixed 
       %% make spanners comprise the note it end on, so that there is no doubt that this note is included.
       \override Score.TrillSpanner #'(bound-details right padding) = #-2
      \override Score.TextSpanner #'(bound-details right padding) = #-1
      %% Lilypond's normal textspanners are too weak:  
      \override Score.TextSpanner #'dash-period = #1
      \override Score.TextSpanner #'dash-fraction = #0.5
      %% lilypond chordname font, like mscore jazzfont, is both far too big and extremely ugly (olagunde@start.no):
      \override Score.ChordName #'font-family = #'roman 
      \override Score.ChordName #'font-size =#0 
      %% In my experience the normal thing in printed scores is maj7 and not the triangle. (olagunde):
      \set Score.majorSevenSymbol = \markup {maj7}
  >>

  %% Boosey and Hawkes, and Peters, have barlines spanning all staff-groups in a score,
  %% Eulenburg and Philharmonia, like Lilypond, have no barlines between staffgroups.
  %% If you want the Eulenburg/Lilypond style, comment out the following line:
  \layout {
    \context {\Score \consists Span_bar_engraver}
    %print-all-headers = ##t
  }
}
\header {
  title = "Canon in D"
  composer = "Johann Pachelbel (1653-1706)"
  copyright = \markup{ \justify{This arrangement is Copyright © 2009 Launceston
Youth and Community Orchestra Inc..  It is licensed under the
Creative Commons Attribution-ShareAlike 3.0 Australia License.  To
view a copy of this license, visit \with-url
#"http://creativecommons.org/licenses/by-sa/3.0/au/"
"http://creativecommons.org/licenses/by-sa/3.0/au/", or write to
Creative Commons, 171 2nd Street, Suite 300, San Francisco,
California, 94105, USA.  This piece is available from the LYCO
Sheet Music Archive (\with-url #"http://sheetmusic.lyco.org.au"
"http://sheetmusic.lyco.org.au").  Revised 3 September 2012.}}

}

}%% end of score-block 


