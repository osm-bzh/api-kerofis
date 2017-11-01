CREATE TABLE kerofis (
    niv numeric(7,0) NOT NULL,
    deiziad_degemer date,
    insee character varying(5),
    kumun character varying(250),
    stagadenn character varying(250),
    lec_hanv character varying(250),
    stumm_orin character varying(250),
    rummad character varying(50),
    stumm_dibab character varying(250),
    deiziad_restr date
);

ALTER TABLE ONLY kerofis
    ADD CONSTRAINT pk_niv PRIMARY KEY (niv);

CREATE INDEX idx_insee ON kerofis USING btree (insee);
CREATE INDEX idx_stumm_didab ON kerofis USING btree (stumm_dibab);
CREATE INDEX idx_stumm_orin ON kerofis USING btree (stumm_orin);
