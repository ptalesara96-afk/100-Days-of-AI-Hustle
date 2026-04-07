from dataclasses import dataclass


@dataclass
class CharacterProfile:
    child_name:      str
    age:             int
    hair_color:      str
    hair_type:       str
    hair_length:     str
    skin_tone:       str
    face_shape:      str
    eye_color:       str
    eye_size:        str
    special_feature: str
    clothing_color:  str
    clothing_style:  str


def build_character_anchor(profile: CharacterProfile) -> str:
    """
    Builds a consistent character description string.
    Used in EVERY image prompt to ensure visual consistency
    across all 8 story pages.
    """
    special = (
        f"with a visible {profile.special_feature},"
        if profile.special_feature.lower() != "none"
        else ""
    )

    return f"""
a {profile.age}-year-old Indian child named
{profile.child_name}, {profile.hair_length}
{profile.hair_type} {profile.hair_color} hair,
{profile.eye_size} {profile.eye_color} eyes,
{profile.face_shape} face shape,
{profile.skin_tone} skin tone, {special}
wearing a {profile.clothing_color}
{profile.clothing_style}, cheerful warm expression,
child-safe appearance
""".strip().replace('\n', ' ')


def build_image_prompt(
    character_anchor: str,
    scene_description: str,
    page_number: int
) -> str:
    """
    Combines character anchor + scene into a full image prompt.
    Art style is fixed — never changes across pages.
    Only scene changes per page.
    """
    return f"""
{character_anchor},
{scene_description}.
Children's book illustration style,
soft watercolour painting, warm pastel colours,
Pixar-inspired warmth, golden hour lighting,
joyful and inviting atmosphere,
wide shot composition, centred subject,
high quality, no text in image,
storybook page format, 4:3 aspect ratio.
Page {page_number} of a children's storybook.
""".strip()