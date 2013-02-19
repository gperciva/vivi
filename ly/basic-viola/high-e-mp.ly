\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "viola-1"
\relative c'' {
  \key e \major
  %\tempo 4 = 108
  \tempo 4 = 72

e4\mp fis gis a b cis dis e

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

