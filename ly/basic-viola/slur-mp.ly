\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "viola-1"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\mp( a b c)
d4( e fis g)
a4( b cis d)
e4( fis gis a)

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

