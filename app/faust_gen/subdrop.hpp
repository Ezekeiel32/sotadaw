/* ------------------------------------------------------------
name: "subdrop"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Subdrop -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Subdrop_H__
#define  __Subdrop_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Subdrop
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class SubdropSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec1[2];
	
  public:
	
	int getNumInputsSubdropSIG0() {
		return 0;
	}
	int getNumOutputsSubdropSIG0() {
		return 1;
	}
	
	void instanceInitSubdropSIG0(int sample_rate) {
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iVec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec1[l4] = 0;
		}
	}
	
	void fillSubdropSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec1[0] = (iVec2[1] + iRec1[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec1[0]));
			iVec2[1] = iVec2[0];
			iRec1[1] = iRec1[0];
		}
	}

};

static SubdropSIG0* newSubdropSIG0() { return (SubdropSIG0*)new SubdropSIG0(); }
static void deleteSubdropSIG0(SubdropSIG0* dsp) { delete dsp; }

static float ftbl0SubdropSIG0[65536];

class Subdrop : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fConst3;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst6;
	float fRec2[2];
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	
 public:
	Subdrop() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Subdrop -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "subdrop.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "subdrop");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		SubdropSIG0* sig0 = newSubdropSIG0();
		sig0->instanceInitSubdropSIG0(sample_rate);
		sig0->fillSubdropSIG0(65536, ftbl0SubdropSIG0);
		deleteSubdropSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 2.2f * fConst0;
		fConst4 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst5 = 1.0f / fConst4;
		fConst6 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.8f);
		fHslider1 = FAUSTFLOAT(0.45f);
		fHslider2 = FAUSTFLOAT(55.0f);
		fHslider3 = FAUSTFLOAT(1.3f);
		fHslider4 = FAUSTFLOAT(0.9f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Subdrop* clone() {
		return new Subdrop();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("subdrop");
		ui_interface->addHorizontalSlider("depth", &fHslider3, FAUSTFLOAT(1.3f), FAUSTFLOAT(0.5f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("fall", &fHslider0, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.1f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("ratio", &fHslider1, FAUSTFLOAT(0.45f), FAUSTFLOAT(0.2f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst3 * fSlow1);
		float fSlow3 = 1.0f / std::max<float>(1.0f, fConst0 * fSlow1);
		float fSlow4 = float(fHslider1);
		float fSlow5 = 1.0f - fSlow4;
		float fSlow6 = fConst6 * float(fHslider2);
		float fSlow7 = float(fHslider3);
		float fSlow8 = 0.85f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec0[1] + (iRec0[1] > 0));
			float fTemp0 = float(iRec0[0]);
			float fTemp1 = ((1 - iVec0[1]) ? 0.0f : fRec2[1] + fSlow6 * (fSlow4 + fSlow5 * std::max<float>(0.0f, std::min<float>(fConst5 * fTemp0, fSlow3 * (fConst4 - fTemp0) + 1.0f))));
			fRec2[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = fSlow8 * tanhf(fSlow7 * ftbl0SubdropSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535))]) * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fSlow2 * (fConst1 - fTemp0) + 1.0f));
			output0[i0] = FAUSTFLOAT(fTemp2);
			output1[i0] = FAUSTFLOAT(fTemp2);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
