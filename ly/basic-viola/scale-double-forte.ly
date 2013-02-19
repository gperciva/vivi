\version "2.13.31"

vlnone = \new Staff {
\relative c {
  \set Staff.instrumentName = "viola-1"
  \key c \major
  \clef alto
  %\tempo 4 = 108
  \tempo 4 = 120

c4\f d e f
g4 a b c
d e f g
a b c d
c2 r2

\bar "|."
}
}

vlntwo = \new Staff {
\relative c {
  \set Staff.instrumentName = "viola-2"
  \key c \major
  \clef alto
  %\tempo 4 = 108
  \tempo 4 = 120

r2 c4\f d
e f g a
b c d e
f g a b
c2 r2

\bar "|."
}
}

\score {
  <<
     \vlnone
     \vlntwo
  >>
  \layout{}
  \midi{}
}

