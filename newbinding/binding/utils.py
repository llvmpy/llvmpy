
def indent_println(println):
    def _println(s):
        println("%s%s" % (' '* 4, s))
    return _println

