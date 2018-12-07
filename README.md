# ModDB Reader

**This library is still WIP, the original library was very limited and just bad overall. I'm rewriting this entirely to be more object oriented in design and to allow to scrap the full site as objects.**

## Finished Models
* Mod
* Game
* Engine
* File
* Media
* Addon
* Article
* Blog
* User

## WIP Models
* Team
* Group
* Job

## Glossary
* **Partial[Model]**: A version of the model which does not contain all the attributes of the full mode. Mainly because that model is being displayed as a preview in another page
* **Boxes**: Containers present on pages, a **div** tag which contains information around a certain theme and as such have been grouped into Box Models of such.
* **Pages**: Another name for Models.
