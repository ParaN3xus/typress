
#let eq = $
  F_( n ) (z)
  & = sum_( m >= 0 ) ( S_( m ) (n) ) / ( m! ) z^( m ) \
  & = sum_( m >= 0 ) sum_( i = 0 )^( n - 1 ) ( i^( m ) z^( m ) ) / ( m! ) \
$

#let display(fonts) = {
  for font in fonts {
    text(font: font)[#font]
    show math.equation: set text(font: font)
    eq
    line(length: 100%)
  }
}

#let fonts = (
  "Asana Math",
  "Cambria Math",
  "DejaVu Math TeX Gyre",
  "New Computer Modern Math",
  "Noto Sans Math",
  "XITS Math",
)
#display(fonts)
