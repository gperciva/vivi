\version "2.13.31"

\include "event-listener.ly"
\include "reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
  \set Staff.midiInstrument = "violin"
\relative c' {
  \key g \major
  \tempo 4 = 72

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlntwo = \new Staff {
  \set Staff.instrumentName = "violin-2"
  \set Staff.midiInstrument = "violin"
\relative c' {
  \key g \major
  \tempo 4 = 72

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlnthree = \new Staff {
  \set Staff.instrumentName = "violin-3"
  \set Staff.midiInstrument = "violin"
\relative c' {
  \key g \major
  \tempo 4 = 72

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlnfour = \new Staff {
  \set Staff.instrumentName = "violin-4"
  \set Staff.midiInstrument = "violin"
\relative c' {
  \key g \major
  \tempo 4 = 72

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlnfive = \new Staff {
  \set Staff.instrumentName = "violin-5"
  \set Staff.midiInstrument = "violin"
\relative c' {
  \key g \major
  \tempo 4 = 72

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

violaone = \new Staff {
  \set Staff.instrumentName = "viola-1"
  \set Staff.midiInstrument = "viola"
\relative c' {
  \key g \major
  \tempo 4 = 72
  \clef alto

r2
g4\f a b c
d e fis g
a b
c d e4 d8 c
b4 c b2


\bar "|."
}
}

violatwo = \new Staff {
  \set Staff.instrumentName = "viola-2"
  \set Staff.midiInstrument = "viola"
\relative c' {
  \key g \major
  \tempo 4 = 72
  \clef alto

r2
g4\f a b c
d e fis g
a b
c d e4 d8 c
b4 c b2


\bar "|."
}
}


celloone = \new Staff {
  \set Staff.instrumentName = "cello-1"
  \set Staff.midiInstrument = "cello"
\relative c {
  \key g \major
  \tempo 4 = 72
  \clef bass

r1
g4\mp a b c
d e fis g
a b c e,
e,4 fis g2

\bar "|."
}
}

cellotwo = \new Staff {
  \set Staff.instrumentName = "cello-2"
  \set Staff.midiInstrument = "cello"
\relative c {
  \key g \major
  \tempo 4 = 72
  \clef bass

r1
g4\mp a b c
d e fis g
a b c e,
e,4 fis g2

\bar "|."
}
}

cellothree = \new Staff {
  \set Staff.instrumentName = "cello-3"
  \set Staff.midiInstrument = "cello"
\relative c {
  \key g \major
  \tempo 4 = 72
  \clef bass

r1
g4\mp a b c
d e fis g
a b c e,
e,4 fis g2

\bar "|."
}
}


\score {
  <<
    \vlnone
    \vlntwo
    \vlnthree
    \vlnfour
    \vlnfive
    \violaone
    \violatwo
    \celloone
    \cellotwo
    \cellothree
  >>
  \layout{}
  \midi{}
}

