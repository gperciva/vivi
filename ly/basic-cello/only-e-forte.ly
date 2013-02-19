\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "cello-1"
\relative c' {
  \key g \major
  \tempo 4 = 60

e4\f fis gis a
e4 fis gis a

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

