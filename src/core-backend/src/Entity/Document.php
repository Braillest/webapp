<?php

namespace App\Entity;

use App\Repository\DocumentRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: DocumentRepository::class)]
class Document
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    private ?string $title = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $content = null;

    #[ORM\Column(length: 255, nullable: true)]
    private ?string $contentType = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $createdAt = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $updatedAt = null;

    /**
     * @var Collection<int, User>
     */
    #[ORM\ManyToMany(targetEntity: User::class)]
    private Collection $author;

    /**
     * @var Collection<int, self>
     */
    #[ORM\ManyToMany(targetEntity: self::class, inversedBy: 'parentDocuments')]
    private Collection $childDocuments;

    /**
     * @var Collection<int, self>
     */
    #[ORM\ManyToMany(targetEntity: self::class, mappedBy: 'childDocuments')]
    private Collection $parentDocuments;

    public function __construct()
    {
        $this->author = new ArrayCollection();
        $this->childDocuments = new ArrayCollection();
        $this->parentDocuments = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getTitle(): ?string
    {
        return $this->title;
    }

    public function setTitle(?string $title): static
    {
        $this->title = $title;

        return $this;
    }

    public function getContent(): ?string
    {
        return $this->content;
    }

    public function setContent(?string $content): static
    {
        $this->content = $content;

        return $this;
    }

    public function getContentType(): ?string
    {
        return $this->contentType;
    }

    public function setContentType(?string $contentType): static
    {
        $this->contentType = $contentType;

        return $this;
    }

    public function getCreatedAt(): ?\DateTimeImmutable
    {
        return $this->createdAt;
    }

    public function setCreatedAt(\DateTimeImmutable $createdAt): static
    {
        $this->createdAt = $createdAt;

        return $this;
    }

    public function getUpdatedAt(): ?\DateTimeImmutable
    {
        return $this->updatedAt;
    }

    public function setUpdatedAt(\DateTimeImmutable $updatedAt): static
    {
        $this->updatedAt = $updatedAt;

        return $this;
    }

    /**
     * @return Collection<int, User>
     */
    public function getAuthor(): Collection
    {
        return $this->author;
    }

    public function addAuthor(User $author): static
    {
        if (!$this->author->contains($author)) {
            $this->author->add($author);
        }

        return $this;
    }

    public function removeAuthor(User $author): static
    {
        $this->author->removeElement($author);

        return $this;
    }

    /**
     * @return Collection<int, self>
     */
    public function getChildDocuments(): Collection
    {
        return $this->childDocuments;
    }

    public function addChildDocument(self $childDocument): static
    {
        if (!$this->childDocuments->contains($childDocument)) {
            $this->childDocuments->add($childDocument);
        }

        return $this;
    }

    public function removeChildDocument(self $childDocument): static
    {
        $this->childDocuments->removeElement($childDocument);

        return $this;
    }

    /**
     * @return Collection<int, self>
     */
    public function getParentDocuments(): Collection
    {
        return $this->parentDocuments;
    }

    public function addParentDocument(self $parentDocument): static
    {
        if (!$this->parentDocuments->contains($parentDocument)) {
            $this->parentDocuments->add($parentDocument);
            $parentDocument->addChildDocument($this);
        }

        return $this;
    }

    public function removeParentDocument(self $parentDocument): static
    {
        if ($this->parentDocuments->removeElement($parentDocument)) {
            $parentDocument->removeChildDocument($this);
        }

        return $this;
    }
}
