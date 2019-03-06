import pytest

import examples
from helpers import make_collector
from stories.exceptions import ContextContractError


# TODO:
#
# [ ] Apply validators to the story arguments on story call.
#
# [ ] Apply substory validators of the substory arguments.
#
# [ ] Context validators should present for every story argument.
#
# [ ] Deny unknown arguments to story call.
#
# [ ] Collect arguments from all substories.  Allow to pass arguments
#     to the substories through story call.
#
# [ ] Set contract in the `ClassMountedStory`.
#
# [ ] Add `contract_in` shortcut.
#
# [ ] Some tests does not check `run` method.
#
# [ ] Some tests calls wrong story methond like `Q().x()` and `J().x()`.


@pytest.mark.parametrize("m", examples.contracts)
def test_context_existed_variables(m):
    """
    We can not write a variable with the same name to the context
    twice.
    """

    class T(m.ChildWithNull, m.StringMethod):
        pass

    class Q(m.ParamParentWithNull, m.NormalParentMethod, T):
        pass

    class J(m.ParamParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These variables are already present in the context: 'bar', 'foo'

Function returned value: T.one

Use different names for Success() keyword arguments.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        T().x(foo=1, bar=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        T().x.run(foo=1, bar=2)
    assert str(exc_info.value) == expected

    # Substory inheritance.

    expected = """
These variables are already present in the context: 'bar', 'foo'

Function returned value: Q.one

Use different names for Success() keyword arguments.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        Q().a(foo=1, bar=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        Q().a.run(foo=1, bar=2)
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These variables are already present in the context: 'bar', 'foo'

Function returned value: T.one

Use different names for Success() keyword arguments.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a(foo=1, bar=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        J().a.run(foo=1, bar=2)
    assert str(exc_info.value) == expected


@pytest.mark.parametrize("m", examples.contracts)
def test_context_variables_normalization(m):
    """
    We apply normalization to the context variables, if story defines
    context contract.  If story step returns a string holding a
    number, we should store a number in the context.
    """

    class T(m.Child, m.StringMethod):
        pass

    class Q(m.ParentWithNull, m.NormalParentMethod, T):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    getter = make_collector()
    T().x()
    assert getter().foo == 1
    assert getter().bar == 2

    # Substory inheritance.

    getter = make_collector()
    Q().x()
    assert getter().foo == 1
    assert getter().bar == 2

    # Substory DI.

    getter = make_collector()
    J().x()
    assert getter().foo == 1
    assert getter().bar == 2


@pytest.mark.parametrize("m", examples.contracts)
def test_context_variables_validation(m):
    """
    We apply validators to the context variables, if story defines
    context contract.
    """

    class T(m.Child, m.WrongMethod):
        pass

    class Q(m.ParentWithNull, m.NormalParentMethod, T):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These variables violates context contract: 'bar', 'foo'

Function returned value: T.one

Violations:

bar:
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        T().x()
    assert str(exc_info.value).startswith(expected)

    # Substory inheritance.

    expected = """
These variables violates context contract: 'bar', 'foo'

Function returned value: Q.one

Violations:

bar:
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        Q().x()
    assert str(exc_info.value).startswith(expected)

    # Substory DI.

    expected = """
These variables violates context contract: 'bar', 'foo'

Function returned value: T.one

Violations:

bar:
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().x()
    assert str(exc_info.value).startswith(expected)


@pytest.mark.parametrize("m", examples.contracts)
def test_arguments_validation_call(m):
    """
    We apply validators to the story arguments, if story defines
    context contract.  This is check performed during story call, not
    execution.
    """

    class T(m.ParamChild, m.NormalMethod):
        pass

    class Q(m.ParamParent, m.NormalParentMethod, m.ChildWithNull, m.NormalMethod):
        pass

    class J(m.ParamParent, m.NormalParentMethod):
        def __init__(self):
            class T(m.ChildWithNull, m.NormalMethod):
                pass

            self.x = T().x

    # Simple.

    expected = """
These arguments violates context contract: 'bar', 'foo'

Story method: T.x

Violations:

bar:
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        T().x(foo="<boom>", bar="<boom>")
    assert str(exc_info.value).startswith(expected)

    with pytest.raises(ContextContractError) as exc_info:
        T().x.run(foo="<boom>", bar="<boom>")
    assert str(exc_info.value).startswith(expected)

    # Substory inheritance.

    expected = """
These arguments violates context contract: 'bar', 'foo'

Story method: Q.a

Violations:

bar:
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        Q().a(foo="<boom>", bar="<boom>")
    assert str(exc_info.value).startswith(expected)

    with pytest.raises(ContextContractError) as exc_info:
        Q().a.run(foo="<boom>", bar="<boom>")
    assert str(exc_info.value).startswith(expected)

    # Substory DI.

    expected = """
These arguments violates context contract: 'bar', 'foo'

Story method: J.a

Violations:

bar:
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a(foo="<boom>", bar="<boom>")
    assert str(exc_info.value).startswith(expected)

    with pytest.raises(ContextContractError) as exc_info:
        J().a.run(foo="<boom>", bar="<boom>")
    assert str(exc_info.value).startswith(expected)


@pytest.mark.parametrize("m", examples.contracts)
def test_context_unknown_variable(m):
    """
    Step can't use Success argument name which was not specified in
    the contract.
    """

    class T(m.Child, m.UnknownMethod):
        pass

    class Q(m.ParentWithNull, m.NormalParentMethod, T):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These variables were not defined in the context contract: 'quiz', 'spam'

Available variables are: 'bar', 'baz', 'foo'

Function returned value: T.one

Use different names for Success() keyword arguments or add these names to the contract.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        T().x()
    assert str(exc_info.value) == expected

    # Substory inheritance.

    expected = """
These variables were not defined in the context contract: 'quiz', 'spam'

Available variables are: 'bar', 'baz', 'foo'

Function returned value: Q.one

Use different names for Success() keyword arguments or add these names to the contract.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        Q().x()
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These variables were not defined in the context contract: 'quiz', 'spam'

Available variables are: 'bar', 'baz', 'foo'

Function returned value: T.one

Use different names for Success() keyword arguments or add these names to the contract.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().x()
    assert str(exc_info.value) == expected


@pytest.mark.parametrize("m", examples.contracts)
def test_context_missing_variables(m):
    """Check story and substory arguments are present in the context."""

    class T(m.ParamChildWithNull, m.NormalMethod):
        pass

    class Q(m.ParentWithNull, m.NormalParentMethod, T):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These variables are missing from the context: bar, foo

Story method: T.x

Story arguments: foo, bar

T.x

Context()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        T().x()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        T().x.run()
    assert str(exc_info.value) == expected

    # Substory inheritance.

    expected = """
These variables are missing from the context: bar, foo

Story method: Q.x

Story arguments: foo, bar

Q.a
  before
  x

Context()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        Q().a()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        Q().a.run()
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These variables are missing from the context: bar, foo

Story method: T.x

Story arguments: foo, bar

J.a
  before
  x (T.x)

Context()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        J().a.run()
    assert str(exc_info.value) == expected
