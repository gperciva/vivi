\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
\relative c' {
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

g4\f a b c
g4\mf a b c
g4\mp a b c
g4\p a b c
\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

