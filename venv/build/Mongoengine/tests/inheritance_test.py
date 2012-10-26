import unittest


class BasesTuple(tuple):
    """Special class to handle introspection of bases tuple in __new__"""
    pass

class DocumentMetaclass(type):
    """Metaclass for all documents.
    """

    def __new__(cls, name, bases, attrs):
        flattened_bases = cls._get_bases(bases)
        super_new = super(DocumentMetaclass, cls).__new__

        if (attrs.get('my_metaclass') == DocumentMetaclass):
            return super_new(cls, name, bases, attrs)
        else:
            attrs['_is_base_cls'] = False

        #
        # Set document hierarchy
        #
        superclasses = ()
        class_name = [name]

        for base in flattened_bases:
            if not hasattr(base, '_class_name'):
                continue

            # Collate heirarchy for _cls and _types
            class_name.append(base.__name__)

        base = flattened_bases[0]

        # Get superclasses from last base superclass
        if hasattr(base, '_class_name'):
            superclasses = base._superclasses
            superclasses += (base._class_name, )

        _cls = '.'.join(reversed(class_name))
        attrs['_class_name'] = _cls
        attrs['_superclasses'] = superclasses
        attrs['_types'] = (_cls, )

        klass = super_new(cls, name, bases, attrs)

        for base in flattened_bases:
            if not hasattr(base, '_class_name'):
                continue
            if _cls not in base._types:
                base._types += (_cls,)

        return klass

    @classmethod
    def _get_bases(cls, bases):
        if isinstance(bases, BasesTuple):
            return bases
        seen = []
        bases = cls.__get_bases(bases)
        unique_bases = (b for b in bases
            if not (b in seen or seen.append(b)))
        return BasesTuple(unique_bases)

    @classmethod
    def __get_bases(cls, bases):
        for base in bases:
            if base is object:
                continue
            yield base
            for child_base in cls.__get_bases(base.__bases__):
                yield child_base


class Document(object):
    __metaclass__ = DocumentMetaclass
    my_metaclass = DocumentMetaclass


class Test(unittest.TestCase):

    def test_inheritance(self):

        class Animal(Document):
            pass

        class Fish(Animal):
            pass

        class Guppy(Fish):
            pass

        class Mammal(Animal):
            pass

        class Human(Mammal):
            pass

        self.assertEqual(Animal._superclasses, ())
        self.assertEqual(Fish._superclasses, ('Animal',))
        self.assertEqual(Guppy._superclasses, ('Animal', 'Animal.Fish'))
        self.assertEqual(Mammal._superclasses, ('Animal',))
        self.assertEqual(Human._superclasses, ('Animal', 'Animal.Mammal'))

        self.assertEqual(Animal._types,
            ('Animal', 'Animal.Fish', 'Animal.Fish.Guppy',
             'Animal.Mammal', 'Animal.Mammal.Human'))
        self.assertEqual(Fish._types, ('Animal.Fish', 'Animal.Fish.Guppy',))
        self.assertEqual(Guppy._types, ('Animal.Fish.Guppy',))
        self.assertEqual(Mammal._types,
            ('Animal.Mammal', 'Animal.Mammal.Human'))
        self.assertEqual(Human._types, ('Animal.Mammal.Human',))

        # Test dynamically adding a class changes the meta data
        class Pike(Fish):
            pass

        self.assertEqual(Pike._superclasses, ('Animal', 'Animal.Fish'))
        self.assertEqual(Pike._types, ('Animal.Fish.Pike',))

        self.assertEqual(Fish._superclasses, ('Animal',))
        self.assertEqual(Fish._types,
            ('Animal.Fish', 'Animal.Fish.Guppy', 'Animal.Fish.Pike'))

        # Test dynamically adding an inherited class changes the meta data
        class Jack(Pike):
            pass

        self.assertEqual(Jack._superclasses,
            ('Animal', 'Animal.Fish', 'Animal.Fish.Pike'))
        self.assertEqual(Jack._types, ('Animal.Fish.Pike.Jack',))

        self.assertEqual(Pike._superclasses, ('Animal', 'Animal.Fish'))
        self.assertEqual(Pike._types,
            ('Animal.Fish.Pike', 'Animal.Fish.Pike.Jack'))

        self.assertEqual(Fish._superclasses, ('Animal',))
        self.assertEqual(Fish._types,
            ('Animal.Fish', 'Animal.Fish.Guppy',
             'Animal.Fish.Pike', 'Animal.Fish.Pike.Jack'))

    def test_mixin_logic(self):

        class Animal(object):
            test = 1

        class Fish(Animal, Document):
            pass

        self.assertEqual(Fish._superclasses, ())
        self.assertEqual(Fish._types, ('Fish', ))

if __name__ == '__main__':
    unittest.main()