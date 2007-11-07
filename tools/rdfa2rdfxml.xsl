<?xml version="1.0" encoding="UTF-8"?>
<stylesheet
    xmlns:xsl  ="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:h    ="http://www.w3.org/1999/xhtml"
    xmlns      ="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf  ="http://www.w3.org/1999/02/22-rdf-syntax-ns#">


<!-- Version 0.4 by Fabien.Gandon@sophia.inria.fr -->


<xsl:output indent="yes" method="xml" media-type="text/plain" encoding="UTF-8" omit-xml-declaration="yes"/>

<!-- uri of the current XHTML page -->
<xsl:param name="this" select="//*/@xml:base[position()=1]"/>


<!-- templates for parsing - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -->

<!--Start the RDF generation-->
<template match="/">
<rdf:RDF xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
  <apply-templates />
</rdf:RDF>
</template>


<!-- match link, meta, span, etc. -->
<template match="*">

   <!-- identify about / suject -->
   <variable name="expanded-about"> 
    <choose>
     <!-- an about was specified on the node or one of its ancestors -->
     <when test="self::*/attribute::about"> 
      <call-template name="expand-curie-or-uri"><with-param name="curie_or_uri" select="ancestor-or-self::*/attribute::about[position()=1]"/></call-template>
     </when>
     <!-- current has a parent with an id -->
     <when test="parent::*/attribute::id"> 
      <value-of select="concat($this,'#',parent::*/attribute::id)"/>
     </when>
     <!-- an about was specified on the node or one of its ancestors -->
     <when test="ancestor::*/attribute::about[position()=1]"> 
      <call-template name="expand-curie-or-uri"><with-param name="curie_or_uri" select="ancestor-or-self::*/attribute::about[position()=1]"/></call-template>
     </when>
     <!-- current node is a meta or a link and the parent is a blank node -->
     <when test="(self::h:link or self::h:meta) and not( parent::h:head )"></when>
     <!-- otherwise and by default we must be talking about the page itself -->
     <otherwise> 
      <value-of select="$this"/>
     </otherwise>
    </choose>
   </variable>
   
   <!-- we have a href and therefore we may have a rel and /or a rev -->
   <if test="@href"> 
     <variable name="expended-href"><call-template name="expand-curie-or-uri"><with-param name="curie_or_uri" select="@href"/></call-template></variable>
     
     <if test="@rel">
       <call-template name="relation">
        <with-param name="subject" select ="$expanded-about" />
        <with-param name="object" select ="$expended-href" />
        <with-param name="predicate" select ="@rel"/>
       </call-template>       
     </if>

     <if test="@rev">
       <call-template name="relation">
        <with-param name="subject" select ="$expended-href" />
        <with-param name="object" select ="$expended-href" />
        <with-param name="predicate" select ="@rev"/>
       </call-template>      
     </if>
     
   </if>
   
   <!-- we have a property -->
   <if test="@property">
     <variable name="expended-pro"><call-template name="expand-ns"><with-param name="qname" select="@property"/></call-template></variable>
      <choose>
       <when test="@content"> <!-- there is a specific content -->
         <call-template name="property">
          <with-param name="subject" select ="$expanded-about" />
          <with-param name="object" select ="@content" />
          <with-param name="datatype" select ="@datatype" />
          <with-param name="predicate" select ="@property"/>
         </call-template>   
       </when>
       <otherwise> <!-- there is no specific content; we use the value of element -->
         <call-template name="property">
          <with-param name="subject" select ="$expanded-about" />
          <with-param name="object" select ="." />
          <with-param name="datatype" select ="@datatype" />
          <with-param name="predicate" select ="@property"/>
         </call-template> 
       </otherwise>
      </choose>
   </if>

   <apply-templates />
</template>


<!-- named templates - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -->

  <!-- return namespace of a qname -->
  <template name="return-ns" >
    <param name="qname" />
    <variable name="ns_prefix" select="substring-before($qname,':')" />
    <variable name="name" select="substring-after($qname,':')" />
    <value-of select="ancestor-or-self::*/namespace::*[name()=$ns_prefix][position()=1]" />
  </template>
  
  <!-- expand namespace of a qname -->
  <template name="expand-ns" >
    <param name="qname" />
    <variable name="ns_prefix" select="substring-before($qname,':')" />
    <variable name="name" select="substring-after($qname,':')" />
    <variable name="ns_uri" select="ancestor-or-self::*/namespace::*[name()=$ns_prefix][position()=1]" />
    <value-of select="concat($ns_uri,$name)" />
  </template>



  <!-- expand CURIE / URI -->
  <template name="expand-curie-or-uri" >
    <param name="curie_or_uri" />
    <choose>
     <when test="starts-with($curie_or_uri,'[')"> <!-- we have a CURIE between square brackets -->
      <call-template name="expand-ns"><with-param name="qname" select="substring-after(substring-before($curie_or_uri,']'),'[')"/></call-template>
     </when>
     <when test="starts-with($curie_or_uri,'#')"> <!-- we have an anchor -->
      <value-of select="concat($this,$curie_or_uri)" />
     </when>
     <when test="string-length($curie_or_uri)=0"> <!-- empty anchor means the document itself -->
      <value-of select="$this" />
     </when>
     <otherwise> <!-- it must be a full URI already -->
      <value-of select="$curie_or_uri" />
     </otherwise>
    </choose>
  </template>  
  
  <!-- generate an RDF statement for a relation -->
  <template name="relation" >
    <param name="subject" />
    <param name="predicate" />
    <param name="object" />
    
    <variable name="predicate-ns"><call-template name="return-ns"><with-param name="qname" select="$predicate"/></call-template></variable>
    
    <element name = "rdf:Description">
      <attribute name="rdf:about"><value-of select="$subject" /></attribute>
      <element name = "{$predicate}" namespace="{$predicate-ns}">
       <attribute name="rdf:resource"><value-of select="$object" /></attribute>
      </element>
    </element>
  </template>

<!-- generate an RDF statement for a property -->
  <template name="property" >
    <param name="subject" />
    <param name="predicate" />
    <param name="object" />
    <param name="datatype" />
    
    <variable name="predicate-ns"><call-template name="return-ns"><with-param name="qname" select="$predicate"/></call-template></variable>
    
    <element name = "rdf:Description">
      <attribute name="rdf:about"><value-of select="$subject" /></attribute>

      <choose>
       <when test="string-length($predicate-ns)>0"> <!-- there is a uri -->
        <element name = "{$predicate}" namespace="{$predicate-ns}">
          <if test="string-length($datatype)>0"> <!-- there is a datatype -->
           <variable name="expended-datatype"><call-template name="expand-ns"><with-param name="qname" select="$datatype"/></call-template></variable>
           <attribute name="rdf:datatype"><value-of select="$expended-datatype" /></attribute>
         </if>
         <value-of select="$object" />
        </element>        
       </when>
       <otherwise> <!-- it must be a full URI already -->
        <element name = "{$predicate}">
          <if test="string-length($datatype)>0"> <!-- there is a datatype -->
           <variable name="expended-datatype"><call-template name="expand-ns"><with-param name="qname" select="$datatype"/></call-template></variable>
           <attribute name="rdf:datatype"><value-of select="$expended-datatype" /></attribute>
         </if>
         <value-of select="$object" />
        </element>
       </otherwise>
      </choose>

     
    </element>
  </template>


<!-- ignore the rest of the DOM -->
<template match="text()|@*"><apply-templates /></template>


</stylesheet>
