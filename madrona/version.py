"""
Used to generated PEP-compliant version numbers
Here's how this works:
The version tuple has 5 components

1. Major version
2. Minor version
3. Revision version
4. Release type: alpha, beta, rc, OR final
5. Release number

The release number is for "re-releasing" code. 
If the release number is > 0, then we get versions like:
    (4,0,0,'beta',2) => 4.0.0b2, etc.

If the Release type is final and the release number is zero:
    (4,0,0,'final',0) => 4.0

If the release number is 0 and the release type is NOT final, we get:
    (4,0,0,'alpha',0) => 4.0dev

If the revision number is > 0, it sneaks in as well:
    (4,0,1,'alpha',0) => 4.0.1dev
"""
VERSION = (4, 1, 0, 'final', 0)
