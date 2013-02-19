\version "2.13.31"

vlnone = \new Staff {
\relative c, {
  \set Staff.instrumentName = "cello-1"
  \key c \major
  \clef bass
  %\tempo 4 = 108
  \tempo 4 = 72

c4\f d e f
g4 a b c
d e f g
a b c d
c2 r2

\bar "|."
}
}

vlntwo = \new Staff {
\relative c, {
  \set Staff.instrumentName = "cello-2"
  \key c \major
  \clef bass
  %\tempo 4 = 108
  \tempo 4 = 72

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

