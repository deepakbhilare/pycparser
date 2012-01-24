import sys
import unittest

# Run from the root dir
sys.path.insert(0, '.')

from pycparser import c_parser, c_generator

_c_parser = c_parser.CParser(
                lex_optimize=False,
                yacc_debug=True, 
                yacc_optimize=False,
                yacctab='yacctab')


def compare_asts(ast1, ast2):
    if type(ast1) != type(ast2):
        return False
    if isinstance(ast1, tuple) and isinstance(ast2, tuple):
        if ast1[0] != ast2[0]:
            return False
        ast1 = ast1[1]
        ast2 = ast2[1]
    for attr in ast1.attr_names:
        if getattr(ast1, attr) != getattr(ast2, attr):
            return False
    for i, c1 in enumerate(ast1.children()):
        if compare_asts(c1, ast2.children()[i]) == False:
            return False
    return True


def parse_to_ast(src):
    return _c_parser.parse(src)


class TestCtoC(unittest.TestCase):
    def _run_c_to_c(self, src):
        ast = parse_to_ast(src)
        generator = c_generator.CGenerator()
        return generator.visit(ast)
    
    def _assert_ctoc_correct(self, src):
        """ Checks that the c2c translation was correct by parsing the code
            generated by c2c for src and comparing the AST with the original
            AST.
        """
        src2 = self._run_c_to_c(src)
        self.assertTrue(compare_asts(parse_to_ast(src), parse_to_ast(src2)), src2)

    def test_trivial_decls(self):
        self._assert_ctoc_correct('int a;')
        self._assert_ctoc_correct('int b, a;')
        self._assert_ctoc_correct('int c, b, a;')
    
    def test_complex_decls(self):
        self._assert_ctoc_correct('int** (*a)(void);')
        self._assert_ctoc_correct('int** (*a)(void*, int);')
    
    def test_casts(self):
        self._assert_ctoc_correct(r'''
            int main() {
                int b = (int) f;
                int c = (int*) f;
            }''')
    
    def test_initlist(self):
        self._assert_ctoc_correct('int arr[] = {1, 2, 3};')

    def test_exprs(self):
        self._assert_ctoc_correct('''
            int main(void)
            {
                int a;
                int b = a++;
                int c = ++a;
                int d = a--;
                int e = --a;
            }''')

    def test_statements(self):
        # note two minuses here
        self._assert_ctoc_correct(r'''
            int main() {
                int a;
                a = 5;
                ;
                b = - - a;
                return a;
            }''')
    
    def test_casts(self):
        self._assert_ctoc_correct(r'''
            int main() {
                int a = (int) b + 8;
                int t = (int) c;
            }
        ''')

    def test_struct_decl(self):
        self._assert_ctoc_correct(r'''
            typedef struct node_t {
                struct node_t* next;
                int data;
            } node;
            ''')
    
    def test_issue36(self):
        self._assert_ctoc_correct(r'''
            int main() {
            }''')
    
    def test_issue37(self):
        self._assert_ctoc_correct(r'''
            int main(void)
            {
              unsigned size;
              size = sizeof(size);
              return 0;
            }''')

        

if __name__ == "__main__":
    unittest.main()

