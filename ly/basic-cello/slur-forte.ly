\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "cello-1"
\relative c, {
  \key c \major
  \clef bass
  \tempo 4 = 120

c4\f( d e f)
g4( a b c)
d4( e f g)
a4( b c d
e d c2)

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

